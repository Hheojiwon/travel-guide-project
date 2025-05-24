from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
store_data = []

def switch_frame(xpath):
    """특정 iframe으로 전환"""
    driver.switch_to.default_content()
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.switch_to.frame(iframe)
    except Exception as e:
        print(f"[iframe 오류] {xpath} 전환 실패:", e)

def get_store_info(store_url):
    driver.get(store_url)
    time.sleep(3)

    try:
        # 왼쪽 리스트 iframe 전환
        switch_frame('//*[@id="searchIframe"]')
        time.sleep(2)

        # 첫 번째 가게 클릭
        first_store = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li[1]/div[1]/div[2]/div[1]/a'))
        )
        first_store.click()
        time.sleep(3)

        # 오른쪽 상세정보 iframe 전환
        switch_frame('//*[@id="entryIframe"]')
        time.sleep(2)
        # 가게명 추출
        try:
            title_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="zD5Nm undefined"]'))
        )
            storename = title_element.find_element(By.XPATH, './/div[1]/div[1]/span[1]').text.strip()
        except Exception:
            storename = "unknown"
            print("[경고] 가게명 없음")

        # 카테고리 추출
        try:
            category = title_element.find_element(By.XPATH, './/div[1]/div[1]/span[2]').text.strip()
        except Exception:
            category = "unknown"
            print("[경고] 카테고리 없음")

        print(f"[가게명] {storename}")
        print(f"[카테고리] {category}")


    
        # 테마 키워드 추출
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        theme_keywords = []
        keyword_blocks = soup.select('div.WXrhH ul.v4tIa li.nc5wr')

        if keyword_blocks:
            for block in keyword_blocks:
                try:
                    theme_type = block.select_one('span.pNnVF').text.strip()
                    keywords = [span.text.strip() for span in block.select('span.sJgQj span')]
                    theme_keywords.append({theme_type: keywords})
                except Exception:
                    continue
        else:
            theme_keywords = "unknown"
            print("[경고] 테마 키워드 없음")

        print(f"[테마 키워드] {theme_keywords}")

        return {
            "storename": storename,
            "category": category,
            "theme_keywords": theme_keywords,
            "url":store_url
        }
        

    except Exception as e:
        print(f"[{store_url}] 크롤링 실패: {e}")
        return {
            "storename": '',
            "category": '',
            "theme_keywords": [],
            "url":store_url
        }
    

import pandas as pd

# CSV 파일 불러오기
df = pd.read_csv("C:/Users/USER/Downloads/V1_관광지_Recommend_url추가.csv")

# URL 리스트 인덱스 설정
store_data = []
for store_url in df['네이버지도URL'][:10]: # 이 부분
    info = get_store_info(store_url)
    store_data.append(info)

# 결과 저장
df_result = pd.DataFrame(store_data)

# 비어 있는 storename 데이터만 따로 추출
df_empty = df_result[df_result['storename'] == '']
df_empty.to_csv("V1_info_missing_1~10.csv", index=False, encoding='utf-8-sig')

# storename이 있는 정상 데이터만 추출
df_valid = df_result[df_result['storename'] != '']
df_valid.to_csv("V1_info_1~10.csv", index=False, encoding='utf-8-sig')

