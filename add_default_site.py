import pandas as pd
from pymongo import MongoClient
from database import valid_jarm_collection

file_path = 'jarm/jarm_alexa_500.csv'
df = pd.read_csv(file_path, usecols=[0, 1, 2], header=None)  # 첫 세 열(A, B, C) 읽기

df.columns = ['host', 'ip', 'result']

df = df[df['result'] != '00000000000000000000000000000000000000000000000000000000000000']
# Failed to resolve IP를 기준으로 하면 IP로 변환은 되는데 접근이 안되는 웹사이트들(pornhub, xnxx 등)의 결과가 제대로 안나오는 것을 처리 못함

json_records = df.to_dict(orient='records')

valid_jarm_collection.insert_many(json_records)
