from pydantic import BaseModel

class RouterDetail(BaseModel):
    service_type : str
    orig_en : str
    orig_tc : str
    orig_sc : str
    dest_en : str
    dest_tc : str
    dest_sc : str

class RouterLane(BaseModel):
    route : str
    bound : str
    router_detail: RouterDetail

class KMBRouter(BaseModel):
    type : str
    version : str
    generated_timestamp : str
    data : list[RouterLane]




