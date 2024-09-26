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
import time

# ChromeDriver 경로 설정
service = Service('C:\\Program Files\\chromedriver.exe')
driver = webdriver.Chrome(service=service)


sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def text_clean(text):
    pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)' # E-mail제거
    text = re.sub(pattern, '', text)
    pattern = r'(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+' # URL제거
    text = re.sub(pattern, '', text)
    pattern = '<[^>]*>'         # HTML 태그 제거
    text = re.sub(pattern, '', text)
    pattern = '[\n]'            # \n제거
    text = re.sub(pattern, '', text)
    pattern = '[\t]'            # \n제거
    text = re.sub(pattern, '', text)
    pattern = '[\']'           
    text = re.sub(pattern, '', text)
    pattern = '[\"]'            
    text = re.sub(pattern, '', text)
    return text  


# 데이터베이스에 index가 어디까지 저장돼있는지 확인하는 함수 필요함
# db에 저장될때 인덱스 중복 방지
def checkMaxNumber() :
    conn = pymysql.connect(
        host='localhost'
        , user='root'
        , password='0000'
        , db='capstone'
        , charset='utf8'
    )
    cur = conn.cursor()

    try:
        # 쿼리 실행
        cur.execute('SELECT MAX(Number) AS maxNumber FROM news')
        # 결과 가져오기
        results = cur.fetchall()
        # 결과 출력 및 MaxNumber 변수에 저장
        if results:
            MaxNumber = results[0][0]  # 첫 번째 행의 첫 번째 컬럼 값을 가져옴
            return(MaxNumber)  # MaxNumber 값을 출력
        else:
            return(0)
    except Exception as e :
            print('Error Message :', e)
            pass
    finally:
        # 커서와 연결을 닫음
        cur.close()
        conn.close()
save_articleCnt=checkMaxNumber() # db에 기사가 몇개까지 저장됐는지

x=dt.datetime.now()
dateCnt=0 # 가져올 날짜범위(개수)
date=int(x.strftime("%Y%m%d"))-1
urlList=[]
num=0

articleCnt=0 # 크롤링할 기사 개수
images=[]
addresses=[]
titles=[]
nums=[]
presses=[]
wdates=[]
articleURLs=[]
summarys=[]
img_list=[]

while dateCnt<2 : # 기사 모든 날짜 출력(지정한 개수의 날짜만큼만)
    url=f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date}"
    res = req.urlopen(url).read().decode('cp949') 
    soup = BeautifulSoup(res, "html.parser")

    #각 날짜를 기준으로 바뀌는 영역
    tr=soup.find('tr',attrs={'align':'center'})
    tds=tr.find_all('td') #첫번째 페이지를 기준으로 해서 td의 갯수를 센다 
    tdsCnt=len(tds)-1 # 맨뒤를 담는 td태그는 갯수에서 제외
    if tdsCnt==0 : tdsCnt=1 # 1페이지만 있는 경우는 맨앞, 맨뒤가 존재하지 않음
    print("\n")

    #날짜에 각 페이지를 기준으로 바뀌는 영역
    cnt=1
    print('---------------------------------------------',date,' 뉴스 링크---------------------------------------------------')
    print("\n")

    while cnt<=tdsCnt : # 하루치 기사만 리스트에 저장
        ur= f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date}&page={cnt}"
        
        # 기사 url 따로 리스트에 저장 (지워도 될듯)
        urlList.insert(num,ur)
        cnt=cnt+1
        num=num+1
        res = req.urlopen(ur).read().decode('cp949') 
        soup = BeautifulSoup(res, "html.parser")
        NewsList=soup.select('#contentarea_left > ul.realtimeNewsList')

        for linkList in NewsList: # 한 페이지의 기사만 리스트에 저장
            links=linkList.select('li')
            for link in links :    
                articleSubjects=link.select('.articleSubject')
                articleSummarys=link.select('.articleSummary')

                for articleSubject in articleSubjects :
                    title=articleSubject.select_one('a').get_text()
                    address=articleSubject.select_one('a').get('href')

                    title=text_clean(title)
                    titles.append(title)
                    addresses.append(address)
                    articleCnt=articleCnt+1 #기사 개수 카운트
                    nums.append(articleCnt+save_articleCnt)
                    #print(articleCnt+save_articleCnt, title)

                for articleSummary in articleSummarys :
                    press=articleSummary.select_one('.press').get_text()
                    wdate=articleSummary.select_one('.wdate').get_text()
                    presses.append(press)
                    wdates.append(wdate)  
    dateCnt=dateCnt+1
    date=date-1

#위의 반복문에서 기간동안의 기사를 모두 리스트에 저장 후 해당 기사 개수만큼 출력
k=0
for k in range(articleCnt) :
    # print("\n\n\nNo.",nums[k]+save_articleCnt, "\ntitle : ",titles[k],
    #         "\npress : " ,presses[k],"\twdate : ",wdates[k])

    a=addresses[k].find('article_id=')#o위치-1 출력
    b=addresses[k].find('&office_id')#&위치-1 출력
    c=addresses[k].find('&mode')#&위치-1 출력
    article_id=addresses[k]
    article_id=article_id[a+11:b]
    office_id=addresses[k]
    office_id=office_id[b+11:c]                
    
    articleURL=f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"

    # requests로 URL 먼저 가져오기
    res=requests.get(articleURL)

    # URL을 리스트에 추가
    articleURLs.append(articleURL)

    # Selenium으로 해당 URL 열기 (새 창이 열리지 않도록)
    driver.get(articleURL)

    try:
        # URL 로딩 대기
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'dic_area')))
        
        # JavaScript로 새 창이 열리는 링크를 수정
        driver.execute_script("document.querySelectorAll('a').forEach(link => { link.onclick = function(event) { event.preventDefault(); }; });")
    
        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 콘텐츠 및 이미지 추출
        content=soup.select_one('#dic_area').get_text()
        image=soup.select_one('#img1')
        if image :
            image_src = image.get('src')
            if image_src:
                print(image_src)
            else:
                print("No src attribute found")
        else :
            image_src = None
            print("No image found")
    except AttributeError as e:
        print("An error occurred:", e)
    content=text_clean(content)
    summarys.append(content)
    images.append(image_src)
driver.quit()
print("\n")

print(type(nums), type(presses), type(wdates), type(articleURLs), type(titles), type(summarys), type(images))


# db에 크롤링한 데이터 저장
def to_dbeaver(nums ,presses, wdates, articleURLs, titles, summarys, images) :
    conn = pymysql.connect(
        host='localhost'
        , user='root'
        , password='0000'
        , db='capstone'
        , charset='utf8'
    )
    cur = conn.cursor()
    
    for num,press,wdate,url,title,summary,image in zip(nums, presses, wdates, articleURLs, titles, summarys, images):
        num=int(num)
        sql = "INSERT INTO news (Number, Press, Wdate, Url, Title, Summary, Image) VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}')".format(
                num, press, wdate, url, title, summary, image)
        try : 
            cur.execute(sql)
            print('insert to DB Success!')
        except Exception as e :
            print('Error Message :', e)
            pass
    conn.commit()
    conn.close()

to_dbeaver(nums, presses, wdates, articleURLs, titles, summarys, images)


