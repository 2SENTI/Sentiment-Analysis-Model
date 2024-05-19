import os
from openai import OpenAI
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm
import time
import numpy as np

# OpenAI API 키값 설정하기
client = OpenAI(api_key="OPENAI API KEY")
df =  pd.read_csv('C:/programming/capstone/finance_data.csv', names=['sentence','kor_sentence'])

# 700~800 데이터만 사용
df = df.iloc[700:800]

# 띄어쓰기 기준으로 영어 리뷰 길이 체크
article_list = []

for article in df['sentence']:
  split= article.split()
  article_list.append(split)

print('기사의 최대 단어 수 :', max(len(article) for article in article_list))
print('기사의 평균 단어 수 :', sum(map(len, article_list))/len(article_list))
plt.hist([len(article) for article in article_list], bins=50)
plt.xlabel('length of article')
plt.ylabel('number of article')
plt.show()

## ChatGPT API를 활용한 감정분석

# 기사를 분석하기 위한 함수 작성
def analyze_article(article):

  try:
    messages = [
            {"role": "system", "content": "너는 기사에 담긴 감정을 분석하고 탐지하는 AI 언어모델이야"},
            {"role": "user", "content": f"다음 기사를 분석해 감정이 긍정인지 부정인지 판단해 알려줘. 대답은 다른 추가적인 설명없이 '긍정' 또는 '부정'  둘 중 하나의 단어로 대답해야 해: {article}"}
            # 퓨샷 러닝을 적용하려면 여기에 긍정/부정의 예시를 함께 넣어줘야 할 듯
            ]


    completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=3,
            n=1,
            stop=None,
            temperature=0
        )

    response= completion.choices[0].message.content
    print(response)
    return response

  except client.error.RateLimitError as e:
    retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
    print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
    time.sleep(retry_time)
    return analyze_article(article)

  except client.error.ServiceUnavailableError as e:
    retry_time = 10  # Adjust the retry time as needed
    print(f"Service is unavailable. Retrying in {retry_time} seconds...")
    time.sleep(retry_time)
    return analyze_article(article)

  except client.error.APIError as e:
    retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
    print(f"API error occurred. Retrying in {retry_time} seconds...")
    time.sleep(retry_time)
    return analyze_article(article)

# 기사 분석해 저장하기
sentiments = []

for article in tqdm(df["sentence"]):
    sentiment = analyze_article(article)
    sentiments.append(sentiment)

df["Sentiment"] = sentiments
df.to_csv("금융뉴스데이터_감정분석결과.csv", index=False)
