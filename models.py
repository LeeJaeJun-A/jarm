from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional


class JarmRequest(BaseModel):
    host: str


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class JarmModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    host: str
    ip: str
    result: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class JarmCreate(BaseModel):
    host: str
    ip: str
    result: str

