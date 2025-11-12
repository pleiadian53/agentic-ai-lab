from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import ConfigDict
from typing import Optional

class EmailCreate(BaseModel):
    recipient: EmailStr
    subject: str
    body: str
    sender: Optional[EmailStr] = None  # Optional sender field

class EmailOut(BaseModel):
    id: int
    sender: EmailStr
    recipient: EmailStr
    subject: str
    body: str
    timestamp: datetime
    read: bool

    model_config = ConfigDict(from_attributes=True) 

