import csv
import time
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
TARGET_URL = "https://www.yellowpages.ca/search/si/1/Real+Estate+Agents/London+ON"
OUTPUT_FILE = "london_leads.csv"


def extract_phone_from_html(html_content):
    """
    Hunts for phone numbers in the raw HTML using multiple patterns.
    """
    # Pattern 1: Look for the 'tel:' link (The most reliable technical source)
    # Matches href="tel:555-555-5555" or similar
    tel_match = re.search(r'tel:([0-9\-\+\(\)\s]+)', html_content)
    if tel_match:
        # Clean up the number (remove "tel:" and quotes if caught)
        clean_num = tel_match.group(1).strip('"').strip("'")
        return clean_num

    # Pattern 2: Look for 'data-phone' attributes often used in these listings
    data_phone_match = re.search(r'data-phone=["\']?([0-9\-\+\(\)\s]+)["\']?', html_content)
    if data_phone_match:
        return data_phone_match.group(1)

    # Pattern 3: Brute force search for (519) ... pattern in the text
    # This is a fallback if the code is obfuscated but text is visible
    text_match = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', html_content)
    if text_match:
        return text_match.group(0)

    return "N/A"


def get_leads():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print(f"[*] Accessing {TARGET_URL}...")
    driver.get(TARGET_URL)
    time.sleep(5)  # Allow JS to load

    # Get all listing cards
    listings = driver.find_elements(By.CLASS_NAME, "listing__content__wrapper")
    print(f"[*] Found {len(listings)} listings. Engaging Nuclear Extraction...")

    data = []

    for item in listings:
        try:
            # 1. Grab the RAW SOURCE code of the individual card
            # This bypasses the need to find specific 'divs' or 'spans'
            card_html = item.get_attribute('innerHTML')

            # 2. Extract Name (Standard method usually works)
            try:
                name = item.find_element(By.CLASS_NAME, "listing__name--link").text
            except:
                name = "Unknown Business"

            # 3. Extract Phone (Using the HTML hunter)
            phone = extract_phone_from_html(card_html)

            # Format cleaning: Remove excess characters if found
            if phone != "N/A":
                phone = urllib.parse.unquote(phone)  # Fix %20 spaces
                phone = re.sub(r'[^\d\-\(\)\s]', '', phone)  # Remove letters if any crept in

            # 4. Extract Address
            try:
                address = item.find_element(By.CLASS_NAME, "listing__address--full").text.replace('\n', ', ')
            except:
                address = "London, ON"

            # LOGGING: Print result so you see it working immediately
            if phone == "N/A":
                print(f"   [!] Failed for {name} (Anti-bot might be hiding it)")
            else:
                print(f"   [+] SUCCESS: {name} | {phone}")
                data.append([name, phone, address])

        except Exception as e:
            print(f"Error on row: {e}")
            continue

    driver.quit()
    return data


def save_to_csv(leads):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Business Name", "Phone", "Address"])
        writer.writerows(leads)
    print(f"\n[DONE] Leads saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    leads = get_leads()
    save_to_csv(leads)