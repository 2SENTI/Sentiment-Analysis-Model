# pip install requests, bs4, pymysql 설치 필요

import requests
from bs4 import BeautifulSoup
import urllib.request as req
import sys
import io
import urllib.parse
import datetime as dt
import pymysql
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# ChromeDriver 경로 설정
service = Service('C:\\Program Files\\chromedriver.exe')
driver = webdriver.Chrome(service=service)

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def text_clean(text):
    pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'  # E-mail 제거
    text = re.sub(pattern, '', text)
    pattern = r'(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'  # URL 제거
    text = re.sub(pattern, '', text)
    pattern = '<[^>]*>'  # HTML 태그 제거
    text = re.sub(pattern, '', text)
    pattern = '[\n]'  # \n 제거
    text = re.sub(pattern, '', text)
    pattern = '[\t]'  # \t 제거
    text = re.sub(pattern, '', text)
    pattern = '[\']'
    text = re.sub(pattern, '', text)
    pattern = '[\"]'
    text = re.sub(pattern, '', text)
    return text

def checkMaxNumber():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='001010',
        db='capstone',
        charset='utf8'
    )
    cur = conn.cursor()

    try:
        cur.execute('SELECT MAX(Number) AS maxNumber FROM news')
        results = cur.fetchall()
        if results:
            MaxNumber = results[0][0]
            return MaxNumber
        else:
            return 0
    except Exception as e:
        print('Error Message :', e)
        pass
    finally:
        cur.close()
        conn.close()

save_articleCnt = 0

# 현재 날짜와 원하는 날짜 범위를 설정 (예: 2020년 1월 1일까지)
x = dt.datetime.now()
end_date = dt.datetime(2020, 1, 1)  # 2020년 1월 1일까지 크롤링
date = x

urlList = []
num = 0

articleCnt = 0
images = []
addresses = []
titles = []
nums = []
presses = []
wdates = []
articleURLs = []
contents = []
img_list = []

while date >= end_date:  # 2020년 1월 1일까지 크롤링
    date_str = date.strftime("%Y%m%d")  # YYYYMMDD 형식으로 날짜 출력
    url = f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date_str}"
    res = req.urlopen(url).read().decode('cp949')
    soup = BeautifulSoup(res, "html.parser")

    tr = soup.find('tr', attrs={'align':'center'})
    tds = tr.find_all('td')
    tdsCnt = len(tds) - 1
    if tdsCnt == 0:
        tdsCnt = 1
    print("\n")

    cnt = 1
    print('---------------------------------------------', date_str, ' 뉴스 링크---------------------------------------------------')
    print("\n")

    while cnt <= tdsCnt:
        ur = f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date_str}&page={cnt}"

        urlList.insert(num, ur)
        cnt += 1
        num += 1
        res = req.urlopen(ur).read().decode('cp949')
        soup = BeautifulSoup(res, "html.parser")
        NewsList = soup.select('#contentarea_left > ul.realtimeNewsList')

        for linkList in NewsList:
            links = linkList.select('li')
            for link in links:
                articleSubjects = link.select('.articleSubject')
                articleSummarys = link.select('.articleSummary')

                for articleSubject in articleSubjects:
                    title = articleSubject.select_one('a').get_text()
                    address = articleSubject.select_one('a').get('href')

                    title = text_clean(title)
                    titles.append(title)
                    addresses.append(address)
                    articleCnt += 1
                    nums.append(articleCnt + save_articleCnt)
                    print(articleCnt + save_articleCnt, title)

                for articleSummary in articleSummarys:
                    press = articleSummary.select_one('.press').get_text()
                    wdate = articleSummary.select_one('.wdate').get_text()
                    presses.append(press)
                    wdates.append(wdate)

    date -= dt.timedelta(days=1)  # 하루씩 줄이기

k = 0
for k in range(articleCnt):
    a = addresses[k].find('article_id=')
    b = addresses[k].find('&office_id')
    c = addresses[k].find('&mode')
    article_id = addresses[k]
    article_id = article_id[a+11:b]
    office_id = addresses[k]
    office_id = office_id[b+11:c]

    articleURL = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"

    res = requests.get(articleURL)
    articleURLs.append(articleURL)

    driver.get(articleURL)

    # 페이지가 완전히 로드될 때까지 대기하는 함수
    def wait_for_page_load(driver, timeout=60):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

    # 시도 횟수 제한
    retries = 3
    while retries > 0:
        try:
            # 페이지 로드 확인
            wait_for_page_load(driver)

            # WebDriverWait 대기 시간을 60초로 늘리고, TimeoutException 발생 시 예외 처리
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'dic_area')))

            # 모든 링크 클릭 방지
            driver.execute_script("document.querySelectorAll('a').forEach(link => { link.onclick = function(event) { event.preventDefault(); }; });")

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            content = soup.select_one('#dic_area').get_text()
            image = soup.select_one('#img1')

            if image:
                image_src = image.get('src')
                if image_src:
                    print(image_src)
                else:
                    print("No src attribute found")
            else:
                image_src = None
                print("No image found")
            break  # 성공적으로 완료된 경우 재시도 중지

        except TimeoutException:
            print(f"TimeoutException: 'dic_area' element not found within 60 seconds at {articleURL}")
            content = "Content could not be loaded due to timeout."
            image_src = None
            retries -= 1  # 시도 횟수 감소
            if retries == 0:
                print("Max retries reached. Skipping this article.")
                break  # 시도 횟수를 초과하면 중단
        except NoSuchElementException as e:
            print(f"NoSuchElementException: {e}")
            content = "Content could not be loaded due to missing elements."
            image_src = None
            break
        except AttributeError as e:
            print(f"AttributeError occurred: {e}")
            content = "Content could not be loaded due to an error."
            image_src = None
            break

    # 텍스트 클리닝 후 리스트에 저장
    content = text_clean(content)
    contents.append(content)
    images.append(image_src)

driver.quit()

print("\n")

print(type(nums), type(presses), type(wdates), type(articleURLs), type(titles), type(contents), type(images))

def to_dbeaver(nums, presses, wdates, articleURLs, titles, contents, images):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='001010',
        db='capstone',
        charset='utf8'
    )
    cur = conn.cursor()

    for num, press, wdate, url, title, content, image in zip(nums, presses, wdates, articleURLs, titles, contents, images):
        num = int(num)
        sql = "INSERT INTO news (Number, Press, Wdate, Url, Title, Contents, Image) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}')".format(
                num, press, wdate, url, title, content, image)
        try:
            cur.execute(sql)
            print('insert to DB Success!')
        except Exception as e:
            print('Error Message :', e)
            pass
    conn.commit()
    conn.close()

to_dbeaver(nums, presses, wdates, articleURLs, titles, contents, images)


