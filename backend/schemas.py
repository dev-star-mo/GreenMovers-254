from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str = Field(min_length=6, max_length=72)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SensorCreate(BaseModel):
    sensor_id: str
    sensor_name: str
    latitude: float = 0.0
    longitude: float = 0.0

class SensorResponse(BaseModel):
    id: int
    sensor_id: str
    sensor_name: str
    latitude: float
    longitude: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    sensor_id: str
    sensor_name: Optional[str] = None
    alert_time: Optional[datetime] = None

class AlertResponse(BaseModel):
    id: int
    sensor_id: str
    sensor_name: str
    alert_time: datetime
    resolved: bool
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    threat_type: Optional[str] = None
    resolution_details: Optional[str] = None
    attachment_path: Optional[str] = None
    
    class Config:
        from_attributes = True

class AlertResolve(BaseModel):
    threat_type: str  # "real" or "false"
    details: str


