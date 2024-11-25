import pymysql
import openai
import time

# OpenAI API 키 설정
openai.api_key = "YOUR_API_KEY"  # 자신의 API 키로 교체

# MySQL 연결 설정 함수 -> 오류 발생 시 재연결을 위해 함수화
def create_connection():
    return pymysql.connect(
        host='hostname',   # 데이터베이스 호스트
        user='username',        # 데이터베이스 사용자
        password='password',        # 데이터베이스 비밀번호
        db='db', # 데이터베이스 이름
        charset='utf8',
    )

# MySQL 연결 생성
conn = create_connection()
cursor = conn.cursor()

# 뉴스 기사 요약 함수
def summarize_article(article):
    try:
        messages = [
            {"role": "system", "content": "너는 기사 내용을 요약하는 AI 언어모델이야."},
            {"role": "system", "content": "기사를 요약했을 때 문장이 어색하지 않고, 문장은 항상 끝맺음이 있어야 하고, 완전한 형태로 작성해줘"},
            {"role": "user", "content": f"다음 기사의 핵심을 요약해줘. 불필요한 내용은 포함하지 말고 중요한 부분을 전달해줘: {article}"}
        ]

        # gpt-3.5-turbo 모델 사용
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,  # 요약에 충분한 토큰 설정
            temperature=0.5
        )

        response = completion.choices[0].message['content'].strip()

        # 출력 검증 -> 요약문이 끝맺음 문장으로 끝나는지 확인
        if not response.endswith(('.', '!', '?')):
            response += " (요약이 잘려서 보완 필요)"
        
        return response

    except Exception as e:
        print(f"OpenAI API error occurred: {e}")
        time.sleep(30)
        return summarize_article(article)

# 특정 범위를 처리하는 함수
def process_articles(start_number, end_number):
    # 데이터베이스에서 특정 범위의 뉴스 기사 가져오기
    cursor.execute(
        "SELECT Number, Contents FROM api_financial_news WHERE Contents IS NOT NULL AND Number BETWEEN %s AND %s",
        (start_number, end_number)
    )
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
            
            conn.commit()
            print(f"[{idx}/{len(rows)}] 요약 완료: {article_number}")

        except pymysql.OperationalError as e:
            print(f"MySQL 연결 오류 발생 ({article_number}): {e}")
            print("연결 재설정 중...")
            
            # 연결 재설정
            conn = create_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE api_financial_news SET Summary = %s WHERE Number = %s",
                (summary, article_number)
            )
            conn.commit()

        except Exception as e:
            print(f"오류 발생 ({article_number}): {e}")
            conn.rollback()  # 현재 작업 롤백

# 범위 설정
start_number = int(input("시작 기사 번호를 입력하세요: "))
end_number = int(input("종료 기사 번호를 입력하세요: "))

# 기사 처리
process_articles(start_number, end_number)

# 연결 종료
cursor.close()
conn.close()

print("뉴스 기사의 요약이 완료되었습니다.")