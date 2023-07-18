from pydantic import BaseModel
from typing import List

class ServiceBase(BaseModel):
  name: str
  description: str = None
  is_active: bool = True

class Service(ServiceBase):
  id: int
  weekday_bandwidth: int | None = None
  weekend_bandwidth: int | None = None

  class Config:
    orm_mode = True

class ListOfServices(BaseModel):
  services: List[Service]

class ServiceUpdate(BaseModel):
  weekday_bandwidth: int | None = None
  weekend_bandwidth: int | None = None

class ServiceCreate(ServiceBase):
  pass