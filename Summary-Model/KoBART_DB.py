from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import pymysql

# 저장된 모델과 토크나이저 로드
model_name = "./fine_tuned_kobart"  # fine-tuned 모델 경로
tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

# MySQL 데이터베이스 연결
def fetch_financial_news():
    conn = pymysql.connect(
        host='hostname', 
        user='username', 
        password='password', 
        db='db', 
        charset='utf8'
    )
    cur = conn.cursor()

    # 뉴스 기사와 내용을 가져옴
    cur.execute("SELECT Number, Title, Contents FROM financial_news")
    rows = cur.fetchall()

    conn.close()
    
    return rows

# 요약 함수
def summarize_text(text, model, tokenizer):
    input_ids = tokenizer.encode(text, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(
        input_ids,
        max_length=128,
        min_length=32,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# 데이터베이스에 Summary 열이 있는지 확인하고 없으면 추가하는 함수
def add_summary_column_if_not_exists():
    conn = pymysql.connect(
        host='hostname', 
        user='username', 
        password='password', 
        db='db', 
        charset='utf8'
    )
    cur = conn.cursor()

    # Summary 열이 없으면 추가
    cur.execute("SHOW COLUMNS FROM financial_news LIKE 'Summary'")
    result = cur.fetchone()

    if result is None:
        cur.execute("ALTER TABLE financial_news ADD COLUMN Summary TEXT")
        conn.commit()

    conn.close()

# 뉴스 데이터 가져오기
financial_news = fetch_financial_news()

# 각 뉴스에 대해 요약 처리
summarized_data = []
for number, title, contents in financial_news:
    summary = summarize_text(contents, model, tokenizer)
    summarized_data.append((number, summary))

# 데이터베이스에 요약 결과 업데이트
def update_summary_in_db(summarized_data):
    conn = pymysql.connect(
        host='hostname', 
        user='username', 
        password='password', 
        db='db', 
        charset='utf8'
    )
    cur = conn.cursor()

    for number, summary in summarized_data:
        sql = "UPDATE financial_news SET Summary = %s WHERE Number = %s"
        cur.execute(sql, (summary, number))

    conn.commit()
    conn.close()

# 1. Summary 열 추가
add_summary_column_if_not_exists()

# 2. 요약 업데이트
update_summary_in_db(summarized_data)
