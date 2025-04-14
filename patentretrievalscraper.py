from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.microsoft import EdgeDriverManager
import time

def get_patent_family_espacenet(patent_number):
    # Setup headless Edge
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")  # Run in headless mode (no UI)
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")

    # Setup Edge WebDriver using webdriver-manager
    driver = webdriver.Edge(service=Service(EdgeDriverManager().install()), options=edge_options)

    try:
        # Step 1: Go to Espacenet search page
        driver.get("https://worldwide.espacenet.com/")

        # Wait and find the search box
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.send_keys(patent_number)

        # Click Search button
        search_button = driver.find_element(By.ID, "searchButton")
        search_button.click()

        # Step 2: Wait for results and click the first one
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result-item"))
        )
        driver.find_element(By.CSS_SELECTOR, ".result-item").click()

        # Step 3: Wait for the details page and click "INPADOC patent family"
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-tab='family']"))
        )
        driver.find_element(By.CSS_SELECTOR, "a[data-tab='family']").click()

        # Step 4: Wait for the family list to load
        family_table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.family-members"))
        )

        # Extract family data
        rows = family_table.find_elements(By.TAG_NAME, "tr")
        family = []
        for row in rows[1:]:  # Skip header
            cols = row.find_elements(By.TAG_NAME, "td")
            if cols:
                country = cols[0].text.strip()
                publication = cols[1].text.strip()
                kind = cols[2].text.strip()
                date = cols[3].text.strip()
                family.append({
                    "country": country,
                    "publication": publication,
                    "kind": kind,
                    "date": date
                })

        return family

    finally:
        driver.quit()


# Example usage:
family = get_patent_family_espacenet("EP1000000")
for f in family:
    print(f)
