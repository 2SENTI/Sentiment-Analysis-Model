import torch
from transformers import BertForSequenceClassification, Trainer, TrainingArguments, BertTokenizer
from sklearn.metrics import accuracy_score, f1_score
import sys
import os

# Preprocessing 폴더를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Preprocessing")))
from BERT_preprocessing import load_and_preprocess_data, tokenize_dataset

# 평가 지표 계산 함수
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = predictions.argmax(axis=1)
    accuracy = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average="weighted")
    return {"accuracy": accuracy, "f1": f1}

# 모델 학습 및 평가 함수
def train_and_evaluate(file_path):
    # 데이터 로딩 및 전처리
    dataset = load_and_preprocess_data(file_path)
    tokenized_datasets = tokenize_dataset(dataset)

    # 모델 설정
    model_name = "bert-base-multilingual-cased"
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)  # 3가지 감정 분류

    # 트레이너 설정
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        compute_metrics=compute_metrics,  # 평가 지표
    )

    # 모델 학습
    trainer.train()

    # 검증 및 테스트 평가
    validation_results = trainer.evaluate()
    test_results = trainer.evaluate(eval_dataset=tokenized_datasets["test"])

    print(f"Validation Results: {validation_results}")
    print(f"Test Results: {test_results}")

    return model, trainer, tokenized_datasets

if __name__ == "__main__":
    file_path = 'C:/Users/windows/Desktop/ESSENTI-Model/Dataset/finance_data.csv'
    model, trainer, tokenized_datasets = train_and_evaluate(file_path)

    # 테스트 데이터셋에 대한 예측 결과 확인
    predictions = trainer.predict(tokenized_datasets["test"])
    print(f"Test Predictions: {predictions.metrics}")
