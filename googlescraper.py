import os
import platform
import subprocess
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Detect default browser
def get_default_browser():
    system_platform = platform.system().lower()

    try:
        if system_platform == 'windows':
            result = subprocess.run(
                ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Shell\\Associations\\URLAssociations\\http\\UserChoice'],
                capture_output=True, text=True, check=True
            )
            if 'chrome' in result.stdout.lower():
                return 'chrome'
            elif 'firefox' in result.stdout.lower():
                return 'firefox'
            elif 'edge' in result.stdout.lower():
                return 'edge'

        elif system_platform == 'darwin':
            result = subprocess.run(['open', '-Ra', 'Safari'], capture_output=True)
            if result.returncode == 0:
                return 'safari'

        elif system_platform == 'linux':
            result = subprocess.run(['xdg-settings', 'get', 'default-web-browser'], capture_output=True, text=True, check=True)
            browser = result.stdout.strip().lower()
            if 'chrome' in browser:
                return 'chrome'
            elif 'firefox' in browser:
                return 'firefox'
            elif 'edge' in browser:
                return 'edge'
    except Exception as e:
        print(f"Error detecting default browser: {e}")

    return None

# Create driver
def create_webdriver(browser):
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    elif browser == 'edge':
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    else:
        raise ValueError("Unsupported browser type")

# Extract patent info
def get_patent_details(index, patent_num, driver):
    print(f"[{index}] Patent: {patent_num}")
    url = f'https://patents.google.com/patent/{patent_num}/en'
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'event')]"))
        )
    except Exception:
        print("Warning: Could not verify event section loaded.")

    def extract(xpath, label):
        try:
            el = driver.find_element(By.XPATH, xpath)
            return el.text.strip()
        except Exception:
            return f"{label} not found"

    return {
        "index": index,
        "patent_number": patent_num,
        "status": extract(
            "//div[contains(@class, 'event') and .//div[text()='Status']]//span[contains(@class, 'title-text')]",
            "Status"
        ),
        "anticipated_expiration_date": extract(
            "//div[contains(@class, 'event') and .//span[contains(text(),'Anticipated expiration')]]/div[contains(@class, 'legal-status')]",
            "Anticipated expiration date"
        ),
        "adjusted_expiration_date": extract(
            "//div[contains(@class, 'event') and .//span[contains(text(),'Adjusted expiration')]]/div[contains(@class, 'legal-status')]",
            "Adjusted expiration date"
        )
    }

# Main execution
main_patent_number = 'US8377085'
output_filename = f'data/{main_patent_number}_extended_family_status.json'

default_browser = get_default_browser()

if default_browser:
    print(f"Default browser detected: {default_browser}")
    driver = create_webdriver(default_browser)

    patent_results = []

    # Process main patent
    patent_results.append(get_patent_details(0, main_patent_number, driver))

    # Process related patents
    family_file = f'data/{main_patent_number}_extended_family.txt'
    if os.path.exists(family_file):
        with open(family_file, 'r') as f:
            for index, line in enumerate(f, start=1):
                patent = line.strip()
                if patent:
                    patent_results.append(get_patent_details(index, patent, driver))
    else:
        print(f"Family file '{family_file}' not found.")

    # Save to JSON
    os.makedirs("data", exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(patent_results, outfile, indent=2, ensure_ascii=False)

    driver.quit()
    print(f"Results saved to {output_filename}")
else:
    print("Unable to detect the default browser. Exiting.")
