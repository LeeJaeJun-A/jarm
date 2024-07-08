from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017")) # 나중에 docker.yaml에다가 MONGODB_URI 설정 or .env 파일 만들고 load_dotenv()
db = client["jarm_database"]
valid_jarm_collection = db["valid_jarm_results"]
malicious_jarm_collection = db["malicious_jarm_results"]
