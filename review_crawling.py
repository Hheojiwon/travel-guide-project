from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

class Crawling:
    def __init__(self, query):
        self.query = query
        self.store_id = self.get_store_id()

    def get_store_id(self):
        url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={self.query}"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        div_tag = soup.find('div', class_='LylZZ')
        a_tag = div_tag.find('a')['href']
        match = re.search(r'place/(\d+)', a_tag)
        return match.group(1)

    def get_info(self):
        info_tabs = {
            "information": "T8RFa",
            "menu/list": "place_section_content",
            "feed": "place_section_content",
            "home": "PIbes",
            "booking": "place_section_content"
        }
        info_result = {}

        for tab, class_name in info_tabs.items():
            url = f"https://pcmap.place.naver.com/restaurant/{self.store_id}/{tab}"
            driver = webdriver.Chrome()
            driver.get(url)
            try: # 수정
                content =  driver.find_element(By.CLASS_NAME, class_name).text # 정보 가져오기
            except NoSuchElementException:
                content = None
            info_result[tab] = content
            driver.quit()

        info_df = pd.DataFrame({key: [value] for key, value in info_result.items()})
        info_df = info_df.dropna(axis=1) 
        return info_df

    def get_reviews(self):
        review_tab = "review/visitor"
        class_name = "pui__vn15t2"
        url = f"https://pcmap.place.naver.com/restaurant/{self.store_id}/{review_tab}"
        driver = webdriver.Chrome()
        driver.get(url)

        # Scroll and load more reviews
        before_h = driver.execute_script("return window.scrollY")
        cnt = 0
        while cnt < 3:
            try:
                load_more_button = driver.find_element(By.XPATH, "//a[@class='fvwqf']")
                load_more_button.click()
                time.sleep(1)
            except:
                pass

            driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.END)
            time.sleep(1)

            after_h = driver.execute_script("return window.scrollY")
            if after_h == before_h:
                break
            before_h = after_h
            cnt += 1

        # Collect reviews
        content = driver.find_elements(By.CLASS_NAME, class_name)
        reviews = [element.text for element in content]
        driver.quit()

        review_df = pd.DataFrame(reviews, columns=['review'])
        return review_df
