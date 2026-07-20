from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any
from datetime import datetime
from app.utils.time import to_tehran_iso

class ClientCreate(BaseModel):
    """Schema for creating a client"""
    name: str = Field(..., max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    percentage: float = Field(..., ge=0, le=100)
    credits_balance: float = Field(default=0.0, ge=0)
    credit_cost_per_lead: Optional[float] = Field(default=1.0, gt=0)
    webhook_url: Optional[str] = None
    google_sheet_id: Optional[str] = None
    accept_webhook: bool = False
    accept_email: bool = False
    accept_sms: bool = False
    accept_sheets: bool = False
    priority_order: Optional[int] = 0
    whatsapp_details_richtext: Optional[str] = None

class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    percentage: Optional[float] = Field(None, ge=0, le=100)
    credits_balance: Optional[float] = Field(None, ge=0)
    credit_cost_per_lead: Optional[float] = Field(None, gt=0)
    webhook_url: Optional[str] = None
    google_sheet_id: Optional[str] = None
    accept_webhook: Optional[bool] = None
    accept_email: Optional[bool] = None
    accept_sms: Optional[bool] = None
    accept_sheets: Optional[bool] = None
    priority_order: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    whatsapp_details_richtext: Optional[str] = None

class ClientResponse(BaseModel):
    """Schema for client response"""
    id: str
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    percentage: float
    credits_balance: float
    status: str
    created_at: datetime
    created_at_tehran: Optional[str] = None
    password_protected_link_token: Optional[str] = None
    password: Optional[str] = None  # For client_password field
    # Delivery methods
    accept_webhook: bool
    accept_email: bool
    accept_sms: bool
    accept_sheets: bool
    webhook_url: Optional[str] = None
    google_sheet_id: Optional[str] = None
    whatsapp_details_richtext: Optional[str] = None
    class Config:
        from_attributes = True

    @classmethod
    def from_client(cls, client):
        """Create ClientResponse from Client model, handling None values"""
        return cls(
            id=str(client.id),
            name=client.name,
            email=client.email,
            phone_number=client.phone_number,
            percentage=client.percentage,
            credits_balance=client.credits_balance,
            status=client.status,
            created_at=client.created_at,
            created_at_tehran=to_tehran_iso(client.created_at),
            password_protected_link_token=client.password_protected_link_token,
            password=client.client_password,
            accept_webhook=client.accept_webhook if client.accept_webhook is not None else False,
            accept_email=client.accept_email if client.accept_email is not None else False,
            accept_sms=client.accept_sms if client.accept_sms is not None else False,
            accept_sheets=client.accept_sheets if client.accept_sheets is not None else False,
            webhook_url=client.webhook_url,
            whatsapp_details_richtext=getattr(client, "whatsapp_details_richtext", None),
            google_sheet_id=client.google_sheet_id
        )
