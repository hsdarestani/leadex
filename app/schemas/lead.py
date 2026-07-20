from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class LeadSubmitRequest(BaseModel):
    """Schema for lead submission from landing page"""
    
    # Required fields
    mobile: str = Field(..., description="Mobile number in E.164 format or local format")
    
    # Optional fields
    name: Optional[str] = Field(None, max_length=255, description="Lead name")
    email: Optional[str] = Field(None, max_length=255, description="Lead email")
    
    # reCAPTCHA token
    recaptcha_token: str = Field(..., description="reCAPTCHA v3 token")
    
    # UTM parameters (optional)
    utm_source: Optional[str] = Field(None, max_length=255)
    utm_medium: Optional[str] = Field(None, max_length=255)
    utm_campaign: Optional[str] = Field(None, max_length=255)
    utm_term: Optional[str] = Field(None, max_length=255)
    utm_content: Optional[str] = Field(None, max_length=255)
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        """Validate mobile number format"""
        if not v:
            raise ValueError("Mobile number is required")
        
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Must contain only digits and optional leading +
        if not re.match(r'^\+?\d{8,15}$', cleaned):
            raise ValueError("Invalid mobile number format")
        
        return cleaned
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format"""
        if v is None:
            return v
        
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")
        
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "mobile": "+971501234567",
                "name": "John Doe",
                "email": "john@example.com",
                "recaptcha_token": "03AGdBq24...",
                "utm_source": "google",
                "utm_medium": "cpc"
            }
        }


class LeadSubmitResponse(BaseModel):
    """Schema for lead submission response"""
    
    success: bool = Field(..., description="Whether submission was successful")
    message: str = Field(..., description="Response message")
    lead_id: Optional[str] = Field(None, description="Lead UUID if successful")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Thank you! Your information has been submitted successfully.",
                "lead_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
