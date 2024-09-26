import requests
from bs4 import BeautifulSoup
import urllib.request as req
import datetime as dt
import re

def text_clean(text):
    pattern = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)' # E-mail제거
    text = re.sub(pattern, '', text)
    pattern = '(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+' # URL제거
    text = re.sub(pattern, '', text)
    pattern = '<[^>]*>'         # HTML 태그 제거
    text = re.sub(pattern, '', text)
    pattern = '[\n]'            # \n제거
    text = re.sub(pattern, '', text)
    pattern = '[\t]'            # \t제거
    text = re.sub(pattern, '', text)
    pattern = '[\']'           
    text = re.sub(pattern, '', text)
    pattern = '[\"]'            
    text = re.sub(pattern, '', text)
    return text  


x = dt.datetime.now()
dateCnt = 0  # 가져올 날짜 범위 (일수)
date = int(x.strftime("%Y%m%d")) - 1  # 어제 날짜부터 시작
urlList = []
num = 0

articleCnt = 0  # 기사 개수 카운트
images = []
addresses = []
titles = []
nums = []
presses = []
wdates = []
articleURLs = []
summarys = []

while dateCnt < 1:  # 하루치 뉴스 기사만 가져옴
    url = f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date}"
    res = req.urlopen(url).read().decode('cp949') 
    soup = BeautifulSoup(res, "html.parser")

    # 날짜별로 기사 링크 리스트 크롤링
    tr = soup.find('tr', attrs={'align': 'center'})
    tds = tr.find_all('td')
    tdsCnt = len(tds) - 1  # 맨뒤 태그 제외
    if tdsCnt == 0: 
        tdsCnt = 1  # 한 페이지만 있을 때
    print("\n")

    cnt = 1
    print('---------------------------------------------', date, ' 뉴스 링크---------------------------------------------------')
    print("\n")

    while cnt <= tdsCnt:  # 각 페이지를 처리
        ur = f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date}&page={cnt}"
        urlList.insert(num, ur)
        cnt += 1
        num += 1
        res = req.urlopen(ur).read().decode('cp949') 
        soup = BeautifulSoup(res, "html.parser")
        NewsList = soup.select('#contentarea_left > ul.realtimeNewsList')

        for linkList in NewsList:  # 페이지에서 뉴스 리스트 크롤링
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
                    articleCnt += 1  # 기사 개수 카운트
                    nums.append(articleCnt)

                for articleSummary in articleSummarys:
                    press = articleSummary.select_one('.press').get_text()
                    wdate = articleSummary.select_one('.wdate').get_text()
                    presses.append(press)
                    wdates.append(wdate)

    dateCnt += 1
    date -= 1

# 크롤링된 결과 출력
for k in range(articleCnt):
    a = addresses[k].find('article_id=')
    b = addresses[k].find('&office_id')
    c = addresses[k].find('&mode')
    article_id = addresses[k][a+11:b]
    office_id = addresses[k][b+11:c]
    
    articleURL = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
    res = requests.get(articleURL)
    articleURLs.append(articleURL)

    html = res.text
    soup = BeautifulSoup(html, "html.parser")
    try:    
        content = soup.select_one('#dic_area').get_text()
    except AttributeError:
        content = ""
    content = text_clean(content)
    summarys.append(content)

    print(f"\nNo. {nums[k]}")
    print(f"Title: {titles[k]}")
    print(f"Press: {presses[k]}")
    print(f"Wdate: {wdates[k]}")
    print(f"URL: {articleURLs[k]}")
    print(f"Summary: {summarys[k]}")
    print("---------------------------------------------------")
