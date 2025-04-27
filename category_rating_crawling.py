import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # 창 없이 실행
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

def get_rating_and_category(place_name):
    try:
        base_url = "https://www.google.com/maps"
        driver.get(base_url)
        time.sleep(2)

        # 검색창에 입력
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(place_name)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

        try:
            parent_element = driver.find_element(By.CLASS_NAME, 'LBgpqf')

            # 별점 가져오기
            try:
                rating_element = parent_element.find_element(By.CLASS_NAME, 'F7nice')
                rating_span = rating_element.find_element(By.XPATH, './/span[@aria-hidden="true"]')
                rating = rating_span.text
            except Exception:
                rating = "정보 없음"

            # 카테고리 가져오기
            try:
                category_element = parent_element.find_element(By.CLASS_NAME, 'DkEaL')
                category = category_element.text
            except Exception:
                category = "정보 없음"

            return rating, category

        except Exception:
            return "정보 없음", "정보 없음"

    except Exception as e:
        print(f"⚠️ '{place_name}' 검색 중 오류 발생: {e}")
        return "정보 없음", "정보 없음"
      


# 드라이버 종료
driver.quit()
print("✅ 모든 평점과 카테고리 저장 완료!")
