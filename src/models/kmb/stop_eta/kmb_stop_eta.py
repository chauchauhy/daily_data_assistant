from pydantic import BaseModel
from typing import Optional


class StopETAData(BaseModel):
    co: str
    route: str
    dir: str
    service_type: int
    seq: int
    dest_tc: str
    dest_sc: str
    dest_en: str
    eta_seq: int
    eta: Optional[str] = None
    rmk_tc: str
    rmk_sc: str
    rmk_en: str
    data_timestamp: str


class KMBStopETAResponse(BaseModel):
    type: str
    version: str
    generated_timestamp: str
    data: list[StopETAData]
