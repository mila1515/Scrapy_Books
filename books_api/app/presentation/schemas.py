from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BookBase(BaseModel):
    title: str
    category: Optional[str] = None
    price: float = Field(..., ge=0.0)
    stock: int = Field(..., ge=0)
    rating: Optional[int] = Field(None, ge=1, le=5)
    url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    stock: Optional[int] = Field(None, ge=0)

class BookSchema(BookBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
