from pydantic import BaseModel
from typing import List, Optional, Union


class RainfallData(BaseModel):
    unit: str
    place: str
    max: int
    main: str


class Rainfall(BaseModel):
    data: List[RainfallData]
    startTime: str
    endTime: str


class TemperatureData(BaseModel):
    place: str
    value: int
    unit: str


class Temperature(BaseModel):
    data: List[TemperatureData]
    recordTime: str


class HumidityData(BaseModel):
    unit: str
    value: int
    place: str


class Humidity(BaseModel):
    recordTime: str
    data: List[HumidityData]


class UVIndexData(BaseModel):
    place: str
    value: Optional[float] = None
    desc: Optional[str] = None
    message: Optional[str] = None


class UVIndex(BaseModel):
    data: List[UVIndexData]
    recordDesc: Optional[str] = None


class HkORHRREADResponse(BaseModel):
    rainfall: Rainfall
    warningMessage: Union[List[str], str] = ""
    icon: List[int]
    iconUpdateTime: str
    uvindex: Union[UVIndex, str] = ""
    updateTime: str
    temperature: Temperature
    tcmessage: str
    mintempFrom00To09: str
    rainfallFrom00To12: str
    rainfallLastMonth: str
    rainfallJanuaryToLastMonth: str
    humidity: Humidity
