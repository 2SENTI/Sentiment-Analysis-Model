import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import BertTokenizer

# 데이터 로딩
def load_and_preprocess_data(file_path):
    train_data = pd.read_csv(file_path)

    # 라벨 맵핑
    label_mapping = {'neutral': 0, 'positive': 1, 'negative': 2}
    train_data['labels'] = train_data['labels'].map(label_mapping)

    # Dataset으로 변환
    train_dataset = Dataset.from_pandas(train_data)

    # 학습/임시 테스트-검증 데이터로 분리
    train_test_data = train_dataset.train_test_split(test_size=0.3)

    # 임시 데이터에서 테스트/검증 데이터로 다시 분리
    test_validation_data = train_test_data['test'].train_test_split(test_size=0.5)

    # 최종 데이터셋 구성
    dataset = DatasetDict({
        'train': train_test_data['train'],
        'test': test_validation_data['test'],
        'validation': test_validation_data['train']  # 나머지 절반은 검증용
    })

    return dataset

# 토크나이징 함수
def tokenize_dataset(dataset, model_name="bert-base-multilingual-cased"):
    tokenizer = BertTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(examples['kor_sentence'], padding="max_length", truncation=True, max_length=128)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    tokenized_datasets.set_format("torch")
    return tokenized_datasets
