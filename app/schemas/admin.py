from pydantic import BaseModel, Field


class AdminLogin(BaseModel):
    """Schema for admin login"""
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class AdminLoginResponse(BaseModel):
    """Schema for admin login response"""
    access_token: str
    token_type: str = "bearer"
    email: str
    role: str
