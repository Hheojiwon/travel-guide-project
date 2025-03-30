import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
import time
import random

def load_restaurant_names(file_name, start=0, end=500):
    try:
        df = pd.read_csv(file_name, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='cp949')
    return df.iloc[start:end, 0].dropna().tolist()

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0')
    options.add_argument('window-size=1380,900')
    options.add_argument('--ignore-certificate-errors')
    return webdriver.Chrome(options=options)

def search_store_on_naver_map(driver, store_name, region=""):
    try:
        search_url = f'https://map.naver.com/v5/search/{region} {store_name}'
        driver.get(search_url)
        sleep(5)
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "entryIframe")))
            driver.switch_to.frame("entryIframe")
        except Exception as e:
            print(f"iframe 전환 실패: {e}")
            return None

        return driver.current_url  
    except Exception as e:
        print(f"검색 오류 {store_name}: {e}")
        return None

def scrape_store_data(driver, store_url):
    try:
        driver.get(store_url)
        sleep(2)
        store_id_match = re.search(r'place/(\d+)', driver.current_url)
        store_id = store_id_match.group(1) if store_id_match else "정보 없음"
        
        url = f"https://pcmap.place.naver.com/restaurant/{store_id}/home/visitor"
        driver.get(url)
        time.sleep(random.uniform(2, 5))
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "place_section_content")))
        
        data = {
            "Store Name": driver.find_element(By.XPATH, '//*[@id="_title"]/div/span[1]').text if driver.find_elements(By.XPATH, '//*[@id="_title"]/div/span[1]') else "정보 없음",
            "Category": driver.find_element(By.XPATH, '//*[@id="_title"]/div/span[2]').text if driver.find_elements(By.XPATH, '//*[@id="_title"]/div/span[2]') else "정보 없음",
            "Address": driver.find_element(By.XPATH, '//span[@class="LDgIH"]').text if driver.find_elements(By.XPATH, '//span[@class="LDgIH"]') else "정보 없음",
            "Phone Number": driver.find_element(By.XPATH, '//span[@class="xlx7Q"]').text if driver.find_elements(By.XPATH, '//span[@class="xlx7Q"]') else "정보 없음",
            "Review": []
        }
        
        review_url = f"https://pcmap.place.naver.com/restaurant/{store_id}/review/visitor"
        driver.get(review_url)
        time.sleep(random.uniform(2, 5))
        
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "place_section_content")))
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            reviews = driver.find_elements(By.CLASS_NAME, "pui__vn15t2")
            data["Review"] = [review.text for review in reviews[:5]] if reviews else ["리뷰 없음"]
        except Exception as e:
            print(f"리뷰 수집 실패: {e}")
            data["Review"] = ["리뷰 없음"]
        
        return data
    except Exception as e:
        print(f"데이터 크롤링 오류 {store_url}: {e}")
        return None

def scrape_restaurants(file_name, output_file, region="", start=0, end=500):
    driver = setup_driver()
    restaurant_names = load_restaurant_names(file_name, start, end)
    store_data = []
    
    for restaurant_name in restaurant_names:
        print(f"검색 중: {restaurant_name}")
        store_url = search_store_on_naver_map(driver, restaurant_name, region)
        if store_url:
            print(f"크롤링 중: {store_url}")
            data = scrape_store_data(driver, store_url)
            if data:
                store_data.append(data)
    
    driver.quit()
    df = pd.DataFrame(store_data)
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"✅ 엑셀 파일 저장 완료: {output_file}")

# 사용 예시
# scrape_restaurants("input.csv", "output.xlsx", region="제주", start=2040, end=3000)
