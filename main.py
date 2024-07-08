import json
import crud
from fastapi import FastAPI, HTTPException
from subprocess import run, PIPE
from models import JarmRequest, JarmModel, JarmCreate
from database import valid_jarm_collection, malicious_jarm_collection


app = FastAPI()


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

    if jarm_result["ip"] is None:
        return {"message": "Failed to resolve IP"}

    existing_result = valid_jarm_collection.find_one({"host": jarm_result["host"]})

    if existing_result:
        if existing_result["result"] == jarm_result["result"]:
            return {"message": "JARM values are the same",
                    "match": True,
                    "valid_result": existing_result["result"]}
        else:  # 다른 경우 jarm_result가 malicious로 판단
            mongo_result = malicious_jarm_collection.insert_one(jarm_result)
            if mongo_result.inserted_id:
                return {"message": "JARM values are not the same",
                        "match": False,
                        "valid_result": existing_result,
                        "malicious_result": jarm_result["result"]
                        }
            else:
                raise HTTPException(status_code=500, detail="Failed to insert data into MongoDB")
    else:
        mongo_result = valid_jarm_collection.insert_one(jarm_result)
        if mongo_result.inserted_id:
            return {"message": "JARM information not found, new data inserted",
                    "match": False,
                    "valid_result": jarm_result["result"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to insert data into MongoDB")


@app.post("/valid_jarm/", response_model=dict)
async def create_valid_jarm(host: str, ip: str, result: str):
    jarm = JarmCreate(host=host, ip=ip, result=result)
    return crud.create_jarm(jarm, "valid")


@app.get("/valid_jarm/{host}", response_model=JarmModel)
async def read_valid_jarm(host: str):
    return crud.read_jarm(host, "valid")


@app.put("/valid_jarm/{host}", response_model=dict)
async def update_valid_jarm(host: str, jarm: str):
    return crud.update_jarm(host, jarm, "valid")


@app.delete("/valid_jarm/{host}", response_model=dict)
async def delete_valid_jarm(host: str):
    return crud.delete_jarm(host, "valid")


@app.post("/malicious_jarm/", response_model=dict)
async def create_malicious_jarm(host: str, ip: str, result: str):
    jarm = JarmCreate(host=host, ip=ip, result=result)
    return crud.create_jarm(jarm, "malicious")


@app.get("/malicious_jarm/{host}", response_model=JarmModel)
async def read_malicious_jarm(host: str):
    return crud.read_jarm(host, "malicious")


@app.put("/malicious_jarm/{host}", response_model=dict)
async def update_malicious_jarm(host: str, jarm: str):
    return crud.update_jarm(host, jarm, "malicious")


@app.delete("/malicious_jarm/{host}", response_model=dict)
async def delete_malicious_jarm(host: str):
    return crud.delete_jarm(host, "malicious")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# ex) http POST http://127.0.0.1:8000/jarm host=www.nexon.com