from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

class PropertyCreate(BaseModel):
    owner_id: int
    name: str
    address: str

class TenantCreate(BaseModel):
    property_id: int
    name: str
    phone: str
    monthly_rent: int
    due_day: int
    is_active: bool = True





