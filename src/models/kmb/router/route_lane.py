from pydantic import BaseModel

class RouterLane(BaseModel):
    route : str
    bound : str
    service_type : str
    orig_en : str
    orig_tc : str
    orig_sc : str
    dest_en : str
    dest_tc : str
    dest_sc : str
    
class KMBRouterResponse(BaseModel):
    type : str
    version : str
    generated_timestamp : str
    data : list[RouterLane]




