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

# Directories
family_data_dir = 'patent_family_data'
status_data_dir = 'patent_status_data'
os.makedirs(status_data_dir, exist_ok=True)

default_browser = get_default_browser()

if default_browser:
    print(f"Default browser detected: {default_browser}")
    driver = create_webdriver(default_browser)

    # Loop through each patent family file
    for file in os.listdir(family_data_dir):
        if not file.endswith('.json'):
            continue

        main_patent_number = file.replace('_extended_family.json', '')
        family_path = os.path.join(family_data_dir, file)
        output_filename = os.path.join(status_data_dir, f"{main_patent_number}_extended_family_status.json")

        try:
            with open(family_path, 'r', encoding='utf-8') as f:
                family_patents = json.load(f)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue

        # Include the main patent too
        all_patents = [main_patent_number] + family_patents
        patent_results = []

        for index, patent in enumerate(all_patents):
            if patent:
                patent_results.append(get_patent_details(index, patent, driver))

        with open(output_filename, 'w', encoding='utf-8') as outfile:
            json.dump(patent_results, outfile, indent=2, ensure_ascii=False)

        print(f"Saved status data for {main_patent_number} with {len(patent_results)} record(s).")

    driver.quit()
    print("Finished processing all patent families.")
else:
    print("Unable to detect the default browser. Exiting.")
