import pandas as pd
from pymongo import MongoClient
from database import valid_jarm_collection

file_path = 'jarm/jarm_alexa_500.csv'
df = pd.read_csv(file_path, usecols=[0, 1, 2], header=None)  # 첫 세 열(A, B, C) 읽기

df.columns = ['host', 'ip', 'result']

df = df[df['ip'] != 'Failed to resolve IP']
# db 지우고
# result == 00000000000000000000000000000000000000000000000000000000000000 이걸 빼자
# pornhub.com 처럼 접근 불가능한 경우 안나옴

json_records = df.to_dict(orient='records')

valid_jarm_collection.insert_many(json_records)
