import os
import platform
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
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
        return webdriver.Chrome(options=options)
    

    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        return webdriver.Firefox( options=options)

    elif browser == 'edge':
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        return webdriver.Edge( options=options)

    else:
        raise ValueError("Unsupported browser type")


# Extract patent info
def get_patent_details(patent_num: str, driver):
    url = f'https://patents.google.com/patent/{patent_num}/en'
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'event')]"))
        )
    except Exception:
        print("Warning: Could not verify event section loaded.")

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
    return loc