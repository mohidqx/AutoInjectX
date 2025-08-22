
import argparse
import asyncio
import aiohttp
import logging
import json
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global list to store results
results = []

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
async def fetch_url(session, url):
    async with session.get(url, timeout=5) as response:
        response.raise_for_status() # Raise an exception for bad status codes
        return await response.text()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(WebDriverException))
async def confirm_xss_with_browser(url, payload):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10) # Set page load timeout
        
        test_url = f"{url}?q={payload}"
        driver.get(test_url)
        
        # Check for alert boxes (common XSS indicator)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            logging.info(f"[!!!] XSS Confirmed (Alert) with payload: {payload} at {test_url} - Alert text: {alert.text}")
            alert.accept()
            return True
        except TimeoutException:
            pass # No alert, continue checking for reflection

        # Check for payload reflection in page source
        if payload in driver.page_source:
            logging.info(f"[+] Potential XSS (Reflection) found with payload: {payload} at {test_url}")
            return True
        else:
            logging.debug(f"[-] Payload not reflected: {payload} at {test_url}")
            return False

    except TimeoutException:
        logging.warning(f"[!] Browser page load timeout for {test_url}")
        return False
    except WebDriverException as e:
        logging.error(f"[!] WebDriver error for {test_url}: {e}")
        return False
    except Exception as e:
        logging.error(f"[!] An unexpected error occurred during browser test for {test_url}: {e}")
        return False
    finally:
        if driver:
            driver.quit()

async def test_xss(session, url, payload, browser_confirmation_enabled):
    is_vulnerable = False
    try:
        test_url = f"{url}?q={payload}"
        response_text = await fetch_url(session, test_url)
        
        if payload in response_text:
            logging.info(f"[+] Potential XSS (Reflection) found with payload: {payload} at {test_url}")
            if browser_confirmation_enabled:
                if await confirm_xss_with_browser(url, payload):
                    is_vulnerable = True
            else:
                is_vulnerable = True # Consider it vulnerable if reflected and browser confirmation is off
        else:
            logging.debug(f"[-] Payload not reflected: {payload} at {test_url}")

    except aiohttp.ClientError as e:
        logging.error(f"[!] HTTP error for {test_url}: {e}")
    except asyncio.TimeoutError:
        logging.warning(f"[!] Timeout for {test_url}")
    except Exception as e:
        logging.error(f"[!] An unexpected error occurred for {test_url}: {e}")
    finally:
        results.append({
            "payload": payload,
            "url": url,
            "vulnerable": is_vulnerable
        })

async def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    target_url = config['Settings']['target_url']
    xss_payloads_file = config['Settings']['xss_payloads_file']
    output_results_file = config['Settings']['output_results_file']
    concurrent_requests = int(config['Settings']['concurrent_requests'])
    browser_confirmation_enabled = config['Settings'].getboolean('browser_confirmation_enabled')

    try:
        with open(xss_payloads_file, "r") as f:
            payloads = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"[!] Payload file not found: {xss_payloads_file}")
        return

    logging.info(f"[*] Starting XSS scan on {target_url} with {len(payloads)} payloads...")

    connector = aiohttp.TCPConnector(limit_per_host=concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for payload in payloads:
            task = asyncio.create_task(test_xss(session, target_url, payload, browser_confirmation_enabled))
            tasks.append(task)
        await asyncio.gather(*tasks)

    logging.info("[*] XSS scan completed.")

    with open(output_results_file, 'w') as f:
        json.dump(results, f, indent=4)
    logging.info(f"[*] Results saved to {output_results_file}")

if __name__ == "__main__":
    asyncio.run(main())


