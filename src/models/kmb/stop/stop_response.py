from pydantic import BaseModel
from typing import List


class Stop(BaseModel):
    stop: str
    name_en: str
    name_tc: str
    name_sc: str
    lat: str
    long: str


class StopListResponse(BaseModel):
    type: str
    version: str
    generated_timestamp: str
    data: List[Stop]