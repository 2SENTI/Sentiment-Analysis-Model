import pymysql
import openai
import time

# OpenAI API 키 설정
openai.api_key = "YOUR_API_KEY"  # 자신의 API 키로 교체

# MySQL 연결 설정
conn = pymysql.connect(
    host='hostname', 
    user='username', 
    password='password',
    db='db', 
    charset='utf8'
)

# 커서 생성
cursor = conn.cursor()

# 뉴스 기사 요약 함수
def summarize_article(article):
    try:
        messages = [
            {"role": "system", "content": "너는 기사 내용을 요약하는 AI 언어모델이야."},
            {"role": "user", "content": f"다음 기사를 핵심만 요약해줘. 중요한 것만 해줘: {article}"}
        ]

        # gpt-3.5-turbo 모델 사용
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,  # 요약 길이를 150 토큰으로 제한
            temperature=0.7
        )

        response = completion.choices[0].message['content']  # 요약된 내용 반환
        return response.strip()

    except Exception as e:
        print(f"OpenAI API error occurred: {e}")
        time.sleep(30)  # 잠시 대기 후 재시도
        return summarize_article(article)

# 데이터베이스에서 뉴스 기사 가져오기
cursor.execute("SELECT Number, Contents FROM financial_news WHERE Contents IS NOT NULL")
rows = cursor.fetchall()

# 요약 결과를 저장할 리스트
summaries = []

# 각 기사 요약 처리
for row in rows:
    article_number = row[0]  # 기사 번호 (Number)
    article_content = row[1]  # 기사 내용
    
    # 기사 요약
    summary = summarize_article(article_content)
    
    # Summary 업데이트
    summaries.append((summary, article_number))

# 요약된 내용 데이터베이스에 업데이트
for summary, article_number in summaries:
    cursor.execute(
        "UPDATE financial_news SET Summary = %s WHERE Number = %s",
        (summary, article_number)
    )

# 커밋하여 변경사항 저장
conn.commit()

# 연결 종료
cursor.close()
conn.close()

print("뉴스 기사의 요약이 완료되었습니다.")