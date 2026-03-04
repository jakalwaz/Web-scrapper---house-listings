import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
# London, ON -> House for Sale -> By Owner
TARGET_URL = "https://www.kijiji.ca/b-house-for-sale/london/c35l1700214?for-sale-by=ownr"
OUTPUT_FILE = "london_fsbo_leads.csv"


def get_fsbo_leads():
    options = webdriver.ChromeOptions()
    # Kijiji is aggressive. These arguments help bypass detection.
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print(f"[*] Accessing Kijiji FSBO Market...")
    driver.get(TARGET_URL)

    # Scroll down to trigger any lazy-loading elements
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(5)

    # --- STRATEGY 1: The "Modern" Layout (data-testid) ---
    listings = driver.find_elements(By.CSS_SELECTOR, "li[data-testid^='listing-card']")

    # --- STRATEGY 2: The "Classic" Layout (search-item class) ---
    if len(listings) == 0:
        print("   [!] Strategy 1 empty. Trying Strategy 2 (Classic Layout)...")
        listings = driver.find_elements(By.CLASS_NAME, "search-item")

    # --- STRATEGY 3: The "Generic" Layout (Any section with a price) ---
    if len(listings) == 0:
        print("   [!] Strategy 2 empty. Trying Strategy 3 (Generic Sections)...")
        # Look for any container that holds a price info
        listings = driver.find_elements(By.XPATH,
                                        "//div[contains(@class, 'price')]//ancestor::div[contains(@class, 'info-container')]")

    print(f"[*] Found {len(listings)} potential leads. Scraping details...")

    data = []

    for item in listings:
        try:
            # We use 'try' blocks for each field because layout varies inside the card

            # TITLE
            try:
                title = item.find_element(By.TAG_NAME, "a").text
                if title == "":  # Sometimes title is hidden or in a nested div
                    title = item.find_element(By.CLASS_NAME, "title").text
            except:
                title = "House for Sale"

            # PRICE
            try:
                # Try finding any element with a dollar sign or 'price' class
                price = item.find_element(By.XPATH, ".//*[contains(text(), '$')]").text
            except:
                price = "Contact for Price"

            # LINK (Crucial)
            try:
                # Usually the main link is on the title
                link_elem = item.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
            except:
                link = "N/A"

            # FILTER: Remove "Wanted" ads or junk
            if "wanted" in title.lower() or link == "N/A":
                continue

            print(f"   -> Found: {title[:30]}... | {price}")
            data.append([title, price, link])

        except Exception as e:
            # print(e) # Uncomment to debug specific errors
            continue

    driver.quit()
    return data


def save_to_csv(leads):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Price", "Link", "Phone Number"])
        writer.writerows(leads)
    print(f"\n[SUCCESS] Saved {len(leads)} leads to {OUTPUT_FILE}")


if __name__ == "__main__":
    leads = get_fsbo_leads()
    if len(leads) > 0:
        save_to_csv(leads)
    else:
        print("\n[FAIL] Still 0 leads. Kijiji might be blocking your IP or requiring a Captcha.")
        print("RECOMMENDATION: Open the URL manually and copy-paste 5 links.")