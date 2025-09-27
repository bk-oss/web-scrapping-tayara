from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import os

def init_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def safe_find_element(element, selectors_list, attribute=None):
    for selector in selectors_list:
        try:
            found_element = element.find_element(By.CSS_SELECTOR, selector)
            if attribute:
                return found_element.get_attribute(attribute)
            return found_element.text.strip()
        except NoSuchElementException:
            continue
    return None

def safe_find_elements(element, selectors_list):
    for selector in selectors_list:
        try:
            found_elements = element.find_elements(By.CSS_SELECTOR, selector)
            if found_elements:
                return found_elements
        except NoSuchElementException:
            continue
    return []

def scrape_cars(start_url, max_pages=260, delay=2):
    driver = init_driver(headless=True)
    driver.get(start_url)

    all_items = []
    page = 1

    while True:
        print(f"--- Page {page} ---")
        
        card_selectors = [
            "article.mx-0",
            "article[class*='mx-']",
            "div[data-testid*='ad-card']",
            "div.ad-card",
            "[class*='card'][class*='ad']",
            "div[class*='listing']"
        ]
        
        cards = []
        for selector in card_selectors:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    print(f"Found {len(cards)} cards using selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        if not cards:
            print("No cards found with any selector, trying to continue...")
            break

        for card in cards:
            try:
                title_selectors = [
                    "h2",
                    "h3",
                    "[class*='title']",
                    "a[class*='title']",
                    ".ad-title",
                    "div[class*='title'] a",
                    "span[class*='title']"
                ]
                title = safe_find_element(card, title_selectors)

                price_selectors = [
                    "span.mr-1",
                    "[class*='price'] span",
                    ".price span",
                    "div[class*='price'] span",
                    "[data-testid*='price'] span",
                    "span[class*='amount']"
                ]
                price_numbers = safe_find_elements(card, price_selectors)
                
                currency_selectors = [
                    "span.text-xs.font-medium",
                    "span[class*='currency']",
                    ".currency",
                    "span.text-xs",
                    "[class*='price'] span[class*='text-xs']"
                ]
                currency = safe_find_element(card, currency_selectors)
                
                if price_numbers:
                    price_text = "".join([s.text.strip() for s in price_numbers if s.text.strip()])
                    price = f"{price_text} {currency}" if currency else price_text
                else:
                    price = None

                city_selectors = [
                    "span.line-clamp-1.truncate",
                    "[class*='location']",
                    ".location",
                    "span[class*='city']",
                    "div[class*='location'] span",
                    "[data-testid*='location']",
                    "span[class*='truncate']"
                ]
                city_text = safe_find_element(card, city_selectors)
                city = city_text.split(",")[0].strip() if city_text else None

                url_selectors = [
                    "a",
                    "a[href*='/ad/']",
                    "[class*='link'] a",
                    "div a[href]"
                ]
                url = safe_find_element(card, url_selectors, attribute="href")

                if title or url:
                    all_items.append({
                        "title": title,
                        "url": url,
                        "price": price,
                        "city": city
                    })

            except Exception as e:
                print(f"Error processing card: {e}")
                continue

        print(f"Extracted {len([item for item in all_items if 'page' not in item or item.get('page', 0) <= page])} items from page {page}")

        if page >= max_pages:
            print("Reached maximum pages requested.")
            break

        next_button_selectors = [
            "button.flex.items-center.justify-center.px-3.h-8.text-sm.font-light.text-neutral-700.border-0.rounded-md",
            "button[class*='next']",
            "[class*='pagination'] button:last-child",
            "button[aria-label*='next']",
            "a[class*='next']",
            ".pagination-next",
            "button[class*='flex'][class*='items-center']:last-of-type"
        ]
        
        next_btn = None
        for selector in next_button_selectors:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if next_btn:
                    break
            except NoSuchElementException:
                continue
        
        if not next_btn:
            print("No next button found with any selector.")
            break
            
        try:
            if ("disabled" in next_btn.get_attribute("class") or 
                not next_btn.is_enabled() or 
                next_btn.get_attribute("disabled")):
                print("Next button disabled, reached last page.")
                break
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(1)
            
            try:
                next_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", next_btn)
            
            time.sleep(delay)
            page += 1
            
        except Exception as e:
            print("No next page or error:", e)
            break

    driver.quit()
    return all_items

def save_to_csv(items, folder_path=r"C:\Users\bkami\OneDrive\Desktop\kol chay", filename="cars_final.csv"):
    if not items:
        print("No items to save.")
        return

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")

    file_path = os.path.join(folder_path, filename)
    keys = ["title", "url", "price", "city"]
    
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(items)

    print(f"Saved {len(items)} ads in {file_path}")

def test_selectors(url):
    driver = init_driver(headless=False)
    driver.get(url)
    
    print("Testing different selectors...")
    
    card_selectors = [
        "article.mx-0",
        "article[class*='mx-']",
        "div[data-testid*='ad-card']",
        "div.ad-card",
        "[class*='card'][class*='ad']"
    ]
    
    for selector in card_selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Selector '{selector}' found {len(cards)} elements")
        except Exception as e:
            print(f"Selector '{selector}' failed: {e}")
    
    input("Press Enter to continue...")
    driver.quit()

if __name__ == "__main__":
    start_url = "https://www.tayara.tn/ads/c/V%C3%A9hicules/?page=1"
    
    # test_selectors(start_url)
    
    data = scrape_cars(start_url, max_pages=20, delay=3)
    save_to_csv(data)
    print("Finished, total ads:", len(data))