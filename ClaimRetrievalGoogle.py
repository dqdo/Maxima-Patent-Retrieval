import os
import platform
import subprocess

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
        options.add_argument("--headless=new")  # disables visibilty of browser
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

# Logging
def log(text, file):
    print(text)
    file.write(text + '\n')

# Extract patent info
def get_patent_details(index, patent_num, driver, log_func):
    log_func(f"[{index}] Patent: {patent_num}")
    url = f'https://patents.google.com/patent/{patent_num}/en'
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'event')]"))
        )
    except Exception:
        log_func("Warning: Could not verify event section loaded.")

    #returns an element given an xpath. If element cannot be found, will return an exception with the label.
    def extract(xpath, label):
        try:
            el = driver.find_elements(By.XPATH, xpath)
            return el
        except Exception:
            return f"{label} not found"
        
    # takes element reference to list of claims and returns string list of claims
    def get_claims_from_ref(reference):
        claims = list()
        for el in reference:
            claims.append(el.text)
        return claims

    claim_text_ref = extract(
        "//patent-text[@name='claims']//section[@id='text']/div[@class='claims style-scope patent-text']/div",
        "Claim text"
    )
    loc = get_claims_from_ref(claim_text_ref)

    log_func(f"Claim text: {loc}")
    log_func("")


# Main execution
main_patent_number = 'US8377085'
output_filename = f'data/{main_patent_number}_extended_family_status.txt'

default_browser = get_default_browser()

if default_browser:
    print(f"Default browser detected: {default_browser}")
    driver = create_webdriver(default_browser)
    output_file = open(output_filename, 'w', encoding='utf-8')

    # Lambda wrapper for logging
    logf = lambda text: log(text, output_file)

    # Process main patent
    get_patent_details(0, main_patent_number, driver, logf)

    # Process related patents
    family_file = f'data/{main_patent_number}_extended_family.txt'
    if os.path.exists(family_file):
        with open(family_file, 'r') as f:
            for index, line in enumerate(f, start=1):
                patent = line.strip()
                if patent:
                    get_patent_details(index, patent, driver, logf)
    else:
        logf(f"Family file '{family_file}' not found.")

    driver.quit()
    output_file.close()
else:
    print("Unable to detect the default browser. Exiting.")
