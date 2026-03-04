import csv
import time
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
BASE_URL = "https://www.yellowpages.ca/search/si/{page}/Real+Estate+Agents/London+ON"
OUTPUT_FILE = "london_agents_mass_list.csv"
PAGES_TO_SCRAPE = 3  # Set to 5 or 10 if you want more


def extract_phone_from_html(html_content):
    # Same "Nuclear" logic that worked before
    tel_match = re.search(r'tel:([0-9\-\+\(\)\s]+)', html_content)
    if tel_match:
        return tel_match.group(1).strip('"').strip("'")

    data_phone_match = re.search(r'data-phone=["\']?([0-9\-\+\(\)\s]+)["\']?', html_content)
    if data_phone_match:
        return data_phone_match.group(1)

    return "N/A"


def get_leads():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_data = []

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        target_url = BASE_URL.format(page=page_num)
        print(f"[*] Accessing Page {page_num}: {target_url}")

        driver.get(target_url)
        time.sleep(4)

        listings = driver.find_elements(By.CLASS_NAME, "listing__content__wrapper")
        print(f"   -> Found {len(listings)} listings. Extracting...")

        for item in listings:
            try:
                card_html = item.get_attribute('innerHTML')

                try:
                    name = item.find_element(By.CLASS_NAME, "listing__name--link").text
                except:
                    name = "Unknown"

                phone = extract_phone_from_html(card_html)

                if phone != "N/A":
                    phone = urllib.parse.unquote(phone)
                    phone = re.sub(r'[^\d\-\(\)\s]', '', phone)

                try:
                    address = item.find_element(By.CLASS_NAME, "listing__address--full").text.replace('\n', ', ')
                except:
                    address = "London, ON"

                print(f"      + {name} | {phone}")
                all_data.append([name, phone, address, "Google Name for Email"])

            except:
                continue

    driver.quit()
    return all_data


def save_to_csv(leads):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Phone", "Address", "Email Action"])
        writer.writerows(leads)
    print(f"\n[SUCCESS] Saved {len(leads)} total leads to {OUTPUT_FILE}")


if __name__ == "__main__":
    leads = get_leads()
    save_to_csv(leads)