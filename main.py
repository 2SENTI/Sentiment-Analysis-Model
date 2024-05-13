import requests
from bs4 import BeautifulSoup
import urllib.request as req
import sys
import io
import urllib.parse
import datetime as dt

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

x=dt.datetime.now()
dateCnt=0 # 가져올 날짜범위(개수)
date=int(x.strftime("%Y%m%d"))
urlList=[]
num=0
while dateCnt<3 : # 기사 모든 날짜 출력(지정한 개수의 날짜만큼만)
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
    while cnt<=tdsCnt : # 기사 하루만 출력
        print('--------------------',cnt,'page 기사 출력----------------------')
        ur= f"https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402&date={date}&page={cnt}"
        
        # 기사 url 따로 리스트에 저장 (지워도 될듯)
        urlList.insert(num,ur)
        cnt=cnt+1
        num=num+1

        res = req.urlopen(ur).read().decode('cp949') 
        soup = BeautifulSoup(res, "html.parser")
        NewsList=soup.select('#contentarea_left > ul.realtimeNewsList')
        for linkList in NewsList: # 기사 한 페이지만 출력
            links=linkList.select('dl > .articleSubject')
            for link in links : # 기사 한개만 출력
                title=link.select_one('a').get_text()
                address=link.select_one('a').get('href')
                print(title, address)
                a=address.find('article_id=')#o위치-1 출력
                b=address.find('&office_id')#&위치-1 출력
                c=address.find('&mode')#&위치-1 출력
                article_id=address[a+11:b]
                office_id=address[b+11:c]
                # print('기사ID:',article_id,' 오피스ID:',office_id)
                    # 기사 한개의 링크인 articleURL로 들어가서 해당 기사 본문 크롤링
                    # address변수로 주소를 써야하는데,,, 문제 발생
                    # 텍스트조합으로 url을 구성할수 있는가?
                # https://n.news.naver.com/mnews/article/{office_id}/{article_id} 형태의 주소임
                
                
                articleURL=f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
                res=requests.get(articleURL)
                html=res.text
                    #res = req.urlopen(articleURL).read().decode('cp949') 
                soup = BeautifulSoup(html, "html.parser")
                try:    
                    content=soup.select_one('#dic_area').get_text()
                except AttributeError as e:
                    #content=soup.select_one('#comp_news_article > div._article_content').get_text()
                    pass
                print('--------본문--------')
                print(content)
        print("\n")

    dateCnt=dateCnt+1
    date=date-1

    # 날짜 계산
    dayFlag=0
    while dayFlag!=1 :
        if 20240101<=date<=20240131 : dayFlag=1
        elif 20240201<=date<=20240229 : dayFlag=1
        elif 20240301<=date<=20240331 : dayFlag=1
        elif 20240401<=date<=20240430 : dayFlag=1
        elif 20240501<=date<=20240531 : dayFlag=1
        else : 
            date=date-1



