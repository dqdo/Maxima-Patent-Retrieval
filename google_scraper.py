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
        return webdriver.Chrome(options=options)

    elif browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    elif browser == 'edge':
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        return webdriver.Edge(options=options)

    else:
        raise ValueError("Unsupported browser type")

# Extract patent info
def get_patent_details(index, patent_num, driver, related_patents=None):
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
        
    # extracts claims from given xpath and label
    def extract_claims(xpath, label):
        try:
            els = driver.find_elements(By.XPATH, xpath)
            claims = list()
            for el in els:
                claims.append(el.text)
            return claims
        except Exception:
            return f"{label} not found"

    return {
        "index": index,
        "patent_number": patent_num,
        "link": driver.current_url,
        "title": extract(
            "//h1[@id='title' and contains(@class, 'scroll-target')"
            " and contains(@class, 'style-scope') and contains(@class, 'patent-result')]",
            "Title"
        ),
        "abstract": extract(
            "//*[@id='text']//abstract/div"
            "[contains(@class, 'abstract') and contains(@class, 'style-scope') and contains(@class, 'patent-text')]",
            "Abstract"
        ),
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
        ),
        "related_patents": related_patents or [],
        "claims": extract_claims(
            "//patent-text[@name='claims']//section[@id='text']/div[@class='claims style-scope patent-text']/div",
            "Claim text"
        )
    }

# Directories
family_data_dir = 'patent_family_data'
status_data_dir = 'patent_status_data'
os.makedirs(status_data_dir, exist_ok=True)

# Load patent family set
family_set_path = os.path.join(family_data_dir, 'patent_family_set.json')

if not os.path.exists(family_set_path):
    print("Error: patent_family_set.json not found.")
    exit()

with open(family_set_path, 'r', encoding='utf-8') as f:
    family_set = json.load(f)

default_browser = get_default_browser()

if default_browser:
    print(f"Default browser detected: {default_browser}")
    driver = create_webdriver(default_browser)

    all_patent_data = []

    for idx, (main_patent, related_patents) in enumerate(family_set.items()):
        try:
            data = get_patent_details(idx, main_patent, driver, related_patents)
            all_patent_data.append(data)
        except Exception as e:
            print(f"Error processing {main_patent}: {e}")

    # Save all results into one file
    final_output_path = os.path.join(status_data_dir, 'patent_family_set_status.json')
    with open(final_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_patent_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved all results to: {final_output_path}")
    driver.quit()
else:
    print("Unable to detect the default browser. Exiting.")
