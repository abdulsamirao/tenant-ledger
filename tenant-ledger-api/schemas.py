from pydantic import BaseModel, Field
from datetime import date
from typing import Literal, Optional

ChargeType = Literal['RENT', 'ELECTRICITY', 'GAS', 'WATER', 'INTERNET', 'OTHER']
ChargeStatus = Literal['UNPAID', 'PARTIALLY_PAID', 'PAID']
PaymentMethod = Literal['CASH','BANK_TRANSFER','EASYPAISA', 'JAZZCASH','OTHER']


class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class PropertyCreate(BaseModel):
    name: str
    address: str

class TenantCreate(BaseModel):
    property_id: int
    name: str
    phone: str
    monthly_rent: int
    rent_due_day: int = Field(ge=1, le=31)
    is_active: bool = True

class ChargeCreate(BaseModel):
    tenant_id: int
    charge_type: ChargeType

    description: Optional[str] = None
    billing_month: date
    amount: float = Field(gt=0)
    due_date: date
    status: ChargeStatus

class PaymentCreate(BaseModel):
    charge_id: int
    amount: float = Field(gt=0)
    payment_method: PaymentMethod
    payment_date: date
    notes: str | None



