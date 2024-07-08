import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from subprocess import run, PIPE
import os


app = FastAPI()

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["jarm_database"]
collection = db["secure_jarm_list"]


class JarmRequest(BaseModel):
    host: str


def generate_jarm(host):
    result = run(["python", "jarm/jarm.py", host, "-j"], stdout=PIPE, stderr=PIPE, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Failed to execute jarm.py: {result.stderr}")

    try:
        jarm_result = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON output: {str(e)}")
    
    return jarm_result


@app.post("/jarm")
def create_jarm(jarm_request: JarmRequest):
    host = jarm_request.host

    jarm_result = generate_jarm(host)
    # Failed to resolve 예외처리

    existing_result = collection.find_one({"host": jarm_result["host"]})

    if existing_result:
        if existing_result["result"] == jarm_result["result"]:
            return {"message": "JARM values are the same",
                    "match": True,
                    "result": existing_result["result"]}
        else:
            return {"message": "JARM values are not the same",
                    "match": False,
                    "current_result": jarm_result,
                    "existing_result": existing_result}
    else:
        mongo_result = collection.insert_one(jarm_result)
        if mongo_result.inserted_id:
            return {"message": "JARM information not found, new document inserted",
                    "match": False,
                    "result": jarm_result}
        else:
            raise HTTPException(status_code=500, detail="Failed to insert data into MongoDB")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)