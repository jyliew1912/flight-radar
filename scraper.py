import time
import json
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database import insert_post
from datetime import datetime, timedelta

def get_date_range(start_date_str, days):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    date_list = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_list.append(current_date.strftime("%Y-%m-%d"))
    return date_list

def apply_baggage_filter(driver):
    print("Indicating checked baggage filter...")
    wait = WebDriverWait(driver, 10)
    
    try:
        # Set data-code="FreeCheckedBaggage" wrapper and clickable label
        wrapper_selector = 'dd[data-code="FreeCheckedBaggage"] div[role="checkbox"]'
        label_selector = 'dd[data-code="FreeCheckedBaggage"] label'
        
        # Wait for the checkbox wrapper to be present
        checkbox_wrapper = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wrapper_selector)))
        
        # Scrool the checkbox into view (centered)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_wrapper)
        time.sleep(1)

        if checkbox_wrapper.get_attribute("aria-checked") == "false":
            target_elem = driver.find_element(By.CSS_SELECTOR, label_selector)
            
            actions = ActionChains(driver)
            actions.move_to_element(target_elem).click().perform()
            print("🖱️ Mouse clicking...")
            time.sleep(1.5)

            time.sleep(8)

        print("✅ Done checked baggage ticked！")
    except Exception as e:
        print(f"❌ Checked baggage ticked failed {e}")


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless=new")  # Close the browser window
    driver = uc.Chrome(options=options, version_main=153, use_subprocess=True)
    return driver

def build_trip_url(d_city, a_city, d_date, quantity=1, currency="TWD"):
    d_city = d_city.lower().strip()
    a_city = a_city.lower().strip()
    
    url = (
        f"https://tw.trip.com/flights/showfarefirst?"
        f"dcity={d_city}&acity={a_city}&ddate={d_date}"
        f"&triptype=ow&class=y&lowpricesource=searchform&quantity={quantity}"
        f"&nonstoponly=off&locale=zh-TW&curr={currency}"
    )
        
    return url

def parse_card_info(card, search_date, quantity, currency):
    flight_data = {
        'date': search_date,
        'airline': '',
        'departure_time': '',
        'arrival_time': '',
        'flight_duration': '',
        'is_direct': '直飛',  
        'has_baggage': '僅手提', 
        'unit_price': '',
        'total_price': '',
        'quantity': quantity,
    }

    # 1. Airline
    airline_elem = card.find(attrs={"data-testid": "flights-name"})
    if airline_elem:
        flight_data['airline'] = airline_elem.get_text(strip=True)

    # 2. Departure and Arrival Times
    time_spans = card.find_all('span', attrs={"data-testid": re.compile(r'flight-time-')})
    if len(time_spans) >= 2:
        flight_data['departure_time'] = time_spans[0].get_text(strip=True)
        flight_data['arrival_time'] = time_spans[1].get_text(strip=True)
    else:
        timer_divs = card.find_all('div', class_=re.compile(r'flight-info-airline__timers'))
        if len(timer_divs) >= 2:
            flight_data['departure_time'] = timer_divs[0].get_text(strip=True)
            flight_data['arrival_time'] = timer_divs[1].get_text(strip=True)

    # 3. Flight Duration
    duration_elem = card.find(attrs={"data-testid": "flightInfoDuration"})
    if duration_elem:
        flight_data['flight_duration'] = duration_elem.get_text(strip=True)

    # 4. Direct Flight Indicator
    stop_elem = card.find(attrs={"data-testid": "stopInfoText"})
    if stop_elem:
        flight_data['is_direct'] = stop_elem.get_text(strip=True)

    # 5. Checked Baggage Information
    checked_baggage_tag = card.find(attrs={"data-testid": "list_label_baggages"}) or \
                          card.find(attrs={"data-label-track": "FREE_CHECKED_BAGGAGE"})
    
    if checked_baggage_tag:
        flight_data['has_baggage'] = checked_baggage_tag.get_text(strip=True)
    else:
        hand_baggage_tag = card.find(attrs={"data-testid": "list_label_hand_baggages"})
        if hand_baggage_tag:
            flight_data['has_baggage'] = hand_baggage_tag.get_text(strip=True)

    # 6. Price
    total_price_elem = card.find(attrs={"data-testid": "flight-total"})

    # Total Price Extraction
    if total_price_elem:
        total_text = total_price_elem.get_text(strip=True)
        match = re.search(r'(?:TWD|NT\$|\$)?\s*([\d,]+)', total_text)
        if match:
            # 取得純數字並轉為 int
            numerical_value = int(match.group(1).replace(',', ''))
            unit_price_value = numerical_value // quantity
            
            # 統一使用 {:,} 格式化千分位
            flight_data['total_price'] = f"{currency} {numerical_value:,}"
            flight_data['unit_price'] = f"{currency} {unit_price_value:,}"
    else:
        price_elem = card.find(attrs={"data-testid": re.compile(r'flight_price_|u_price_info')})
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            match = re.search(r'(?:TWD|NT\$|\$)?\s*([\d,]+)', price_text)
            if match:
                unit_val = int(match.group(1).replace(',', ''))
                formatted_price = f"{currency} {unit_val:,}"
                flight_data['unit_price'] = formatted_price
                flight_data['total_price'] = formatted_price
            else:
                flight_data['unit_price'] = price_text
                flight_data['total_price'] = price_text

    # 7. Quantity
    flight_data['quantity'] = quantity

    return flight_data


# ========================== FLIGHT EXTRACTION FUNCTION ==========================
def extract_flights(url, search_date, driver, need_baggage, top_n, quantity, currency):
    print(f"🌐 Waiting for page to load: {url}")
    driver.get(url)

    # time.sleep(20)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid*='flight-card'], div.result-item"))
    )

    # Checked baggage filter application
    if need_baggage:
        apply_baggage_filter(driver)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find flight cards
    cards = soup.find_all('div', class_=re.compile(r'result-item\s+J_FlightItem'))
    if not cards:
        cards = soup.find_all('div', attrs={"data-testid": re.compile(r'u-flight-card')})

    print(f"🔍 Found {len(cards)} flight cards on the page. Starting to extract {top_n}...")

    results = []
    for card in cards:
        data = parse_card_info(card, search_date, quantity, currency)
        data['url'] = url
            
        results.append(data)
        
        if len(results) >= top_n:
            break

    return results

#  ========================== MAIN EXECUTION ==========================
def main(start_date="2027-02-25", days_to_scrape=3, departure_city="syd", arrival_city="kul", currency="TWD", quantity=1, top_n=4, need_baggage=True):

    dates = get_date_range(start_date, days_to_scrape)
    driver = init_driver()

    for current_date in dates:
        print(f"\n🚀 Starting to scrape flights for {current_date}...")
        test_url = build_trip_url(
            d_city=departure_city,
            a_city=arrival_city,
            d_date=current_date,  
            quantity=quantity,
            currency=currency
        )

        top_4_flights = extract_flights(test_url, current_date, driver, need_baggage, top_n, quantity, currency)
        
        print("\n" + "="*50)
        print(f"🎉 Successfully extracted {current_date} before {len(top_4_flights)} flight records (Quantity: {quantity}):")
        print("="*50)
        print(json.dumps(top_4_flights, ensure_ascii=False, indent=2))
        insert_post(top_4_flights, departure_city, arrival_city, currency)

       
    try:
        driver.quit()
    except Exception:
        pass


if __name__ == "__main__":
    main()
