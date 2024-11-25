import pymysql
import openai
import time

# OpenAI API 키 설정
openai.api_key = "YOUR_API_KEY"  # 자신의 API 키로 교체

# MySQL 연결 설정 함수 -> 오류 발생 시 재연결을 위해 함수화
def create_connection():
    return pymysql.connect(
        host='hostname', 
        user='username', 
        password='password',
        db='db', 
        charset='utf8'
    )

# MySQL 연결 생성
conn = create_connection()
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
            max_tokens=150,
            temperature=0.7
        )

        response = completion.choices[0].message['content']  # 요약된 내용 반환
        return response.strip()

    except Exception as e:
        print(f"OpenAI API error occurred: {e}")
        time.sleep(30)  # 잠시 대기 후 재시도
        return summarize_article(article)

# 데이터베이스에서 뉴스 기사 가져오기
cursor.execute("SELECT Number, Contents FROM api_financial_news WHERE Contents IS NOT NULL")
rows = cursor.fetchall()

# 각 기사 처리
for idx, row in enumerate(rows, 1):
    article_number = row[0]  # 기사 번호
    article_content = row[1]  # 기사 내용

    try:
        # 기사 요약 생성
        summary = summarize_article(article_content)
        
        # 데이터베이스 업데이트
        cursor.execute(
            "UPDATE api_financial_news SET Summary = %s WHERE Number = %s",
            (summary, article_number)
        )
        
        # 작업 단위 커밋 - 개별 작업 저장
        conn.commit()
        print(f"[{idx}/{len(rows)}] 요약 완료: {article_number}")

    except pymysql.OperationalError as e:
        print(f"MySQL 연결 오류 발생 ({article_number}): {e}")
        print("연결 재설정 중...")
        
        # 연결 재설정
        conn = create_connection()
        cursor = conn.cursor()
        
        # 작업 다시 시도
        cursor.execute(
            "UPDATE api_financial_news SET Summary = %s WHERE Number = %s",
            (summary, article_number)
        )
        conn.commit()

    except Exception as e:
        print(f"오류 발생 ({article_number}): {e}")
        conn.rollback()  # 현재 작업 롤백

# 연결 종료
cursor.close()
conn.close()

print("뉴스 기사의 요약이 완료되었습니다.")