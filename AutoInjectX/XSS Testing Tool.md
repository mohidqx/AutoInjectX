# XSS Testing Tool

A powerful and efficient command-line interface (CLI) tool for automated Cross-Site Scripting (XSS) vulnerability testing. This tool is designed to help security researchers and developers identify XSS vulnerabilities in web applications by testing a large number of payloads against a target URL.

## Features

- **Asynchronous Scanning:** Achieves high performance by scanning multiple URLs concurrently.
- **Headless Browser Confirmation:** Confirms XSS vulnerabilities by executing payloads in a headless browser environment, detecting JavaScript alerts and DOM reflections.
- **Robust Error Handling & Retries:** Implements retry mechanisms for network issues and robust error handling to ensure scan completion.
- **Configurable Settings:** Easily customize scan parameters, target URLs, and payload files via a `config.ini` file.
- **Results Export:** Saves scan results to a JSON file for easy analysis and reporting.
- **Payload Extraction:** Ability to extract XSS payloads from a given website URL and save them to a local file.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Note: You might need to create a `requirements.txt` file with `pip freeze > requirements.txt` after installing all dependencies like `aiohttp`, `selenium`, `tenacity`, `configparser`)

3.  **Install Chromium Browser:**
    This tool uses Chromium for headless browser testing. Make sure you have it installed on your system.
    
    **For Ubuntu/Debian:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y chromium-browser
    ```

## Usage

1.  **Configure `config.ini`:**
    Before running the tool, open `config.ini` and adjust the settings according to your needs:
    ```ini
    [Settings]
    target_url = http://example.com
    xss_payloads_file = xss_payloads.txt
    output_results_file = xss_results.json
    concurrent_requests = 100
    browser_confirmation_enabled = True

    [Retries]
    max_attempts = 3
    wait_seconds = 2
    ```

2.  **Run the tool:**
    ```bash
    python3 xss_tester.py
    ```

    The tool will read the `target_url` and `xss_payloads_file` from `config.ini` and start the scan.

## Payload File Format

The `xss_payloads.txt` file should contain one XSS payload per line.

Example `xss_payloads.txt`:
```
<script>alert(1)</script>
<img src=x onerror=alert(1)>
"><svg onload=alert(1)>
```

## Results

Scan results will be saved to the file specified in `output_results_file` (default: `xss_results.json`). The JSON output will contain a list of dictionaries, each representing a tested payload and its vulnerability status.

Example `xss_results.json`:
```json
[
    {
        "payload": "<script>alert(1)</script>",
        "url": "http://example.com",
        "vulnerable": true
    },
    {
        "payload": "<img src=x onerror=alert(1)>",
        "url": "http://example.com",
        "vulnerable": false
    }
]
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


