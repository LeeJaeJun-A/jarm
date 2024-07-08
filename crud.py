from bson import ObjectId
from fastapi import HTTPException
from models import JarmCreate
from database import valid_jarm_collection, malicious_jarm_collection


async def get_collection(jarm_type: str):
    if jarm_type == "valid":
        return valid_jarm_collection
    elif jarm_type == "malicious":
        return malicious_jarm_collection
    else:
        raise ValueError("Invalid jarm_type")


async def create_jarm(jarm: JarmCreate, jarm_type: str):
    collection = await get_collection(jarm_type)
    jarm_dict = jarm.dict()
    jarm_dict["_id"] = ObjectId()
    await collection.insert_one(jarm_dict)
    return {"message": "JARM is successfully created"}


async def read_jarm(host: str, jarm_type: str):
    collection = await get_collection(jarm_type)
    jarm = await collection.find_one({"host": host})
    if jarm is None:
        raise HTTPException(status_code=404, detail="JARM not found")
    return jarm


async def update_jarm(host: str, jarm: str, jarm_type: str):
    collection = await get_collection(jarm_type)
    result = await collection.update_one({"host": host}, {"$set": {"result": jarm}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="JARM not found")
    return {"message": "JARM is successfully updated"}


async def delete_jarm(host: str, jarm_type: str):
    collection = await get_collection(jarm_type)
    result = await collection.delete_one({"host": host})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="JARM not found")
    return {"message": "JARM is successfully deleted"}

