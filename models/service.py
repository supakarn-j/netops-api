from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=True, nullable=True)
    is_active = Column(Boolean, default=True)

    weekday_bandwidth = Column(Integer, index=True, nullable=True)
    weekend_bandwidth = Column(Integer, index=True, nullable=True)