import os
from openai import OpenAI
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm
import time
import numpy as np
# Classification Report
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, \
                            roc_auc_score, confusion_matrix, classification_report, \
                            matthews_corrcoef, cohen_kappa_score, log_loss

# OpenAI API 키값 설정하기
client = OpenAI(api_key="OPENAI API KEY")
df =  pd.read_csv('C:/programming/capstone/finance_data.csv', names=['sentence','kor_sentence'])

df =  pd.read_csv('C:/programming/capstone/finance_data_output.csv')

df=df.loc[:,['labels','kor_sentence','Sentiment']]
df['labels']=df['labels'].replace(['neutral','positive','negative'],[0,1,2])
df['Sentiment']=df['Sentiment'].replace(['neutral','positive','negative'],[0,1,2])

df.head()

df.info()

df[df['kor_sentence'].duplicated()]

DATASET_PREP_FILE = 'C:/programming/capstone/dataset_prep.csv'
df.drop_duplicates(subset=['kor_sentence'],inplace=True)
df.to_csv(DATASET_PREP_FILE) # 구글 드라이브 폴더에 저장

#  7. 라벨별 데이터 개수 확인
df['labels'].value_counts().plot(kind='bar')
plt.xlabel("Label")
plt.ylabel("Number")

# 8. 라벨별 데이터 비율 확인
df['labels'].value_counts(normalize=True)

# 9. 감정 분류 모델 성능 평가
df['Sentiment']=df['Sentiment'].astype('int')

predicted_value = df['Sentiment']
label = df['labels']
print(df.dtypes)

# Classification Report
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, \
                            roc_auc_score, confusion_matrix, classification_report, \
                            matthews_corrcoef, cohen_kappa_score, log_loss

cl_report = classification_report(label, predicted_value, output_dict=True)
cl_report_df = pd.DataFrame(cl_report).transpose()
cl_report_df = cl_report_df.round(3)
print(cl_report_df)

accuracy_score_v = round(accuracy_score(label, predicted_value), 3) # Accuracy
precision_score_v = round(precision_score(label, predicted_value, average="weighted"), 3) # Precision
recall_score_v = round(recall_score(label, predicted_value, average="weighted"), 3) # Recall
f1_score_v = round(f1_score(label, predicted_value, average="weighted"), 3) # F1 Score

# 평가지표 결과 저장
METRIC_FILE = 'C:/programming/capstone/metric.csv'

metric_total = pd.DataFrame({
    'PLM': 'chatgpt3.5-turbo',
    'Accuracy': accuracy_score_v,
    'Precision': precision_score_v,
    'Recall': recall_score_v,
    'F1_score': f1_score_v},
    index = ['-']
    )

metric_total.to_csv(METRIC_FILE)