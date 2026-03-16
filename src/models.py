from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ObligationCode(str, Enum):
    INCOME_TAX_COMPANY = "4"
    INCOME_TAX_PAYE = "7"
    VAT = "9"
    INCOME_TAX_WITHHOLDING = "6"


class TaxpayerDetails(BaseModel):
    TaxpayerPIN: str = Field(..., description="KRA PIN number (format: A000000000L)")
    ObligationCode: str = Field(..., description="Tax obligation type")
    Month: str = Field(..., description="Month (01-12)")
    Year: str = Field(..., description="Year (e.g., 2024)")

    @field_validator("ObligationCode")
    @classmethod
    def validate_obligation_code(cls, v):
        valid_codes = ["4", "6", "7", "9"]
        if v not in valid_codes:
            raise ValueError(f"Invalid obligation code. Must be one of: {', '.join(valid_codes)}")
        return v

    @field_validator("TaxpayerPIN")
    @classmethod
    def validate_pin(cls, v):
        if not v or len(v) != 11:
            raise ValueError("Invalid PIN format. Expected format: A000000000L")
        if not v[0].isalpha() or not v[-1].isalpha():
            raise ValueError("PIN must start and end with a letter")
        if not v[1:-1].isdigit():
            raise ValueError("PIN must contain 9 digits between letters")
        return v.upper()

    @field_validator("Month")
    @classmethod
    def validate_month(cls, v):
        month = int(v)
        if month < 1 or month > 12:
            raise ValueError("Month must be between 01 and 12")
        return str(month).zfill(2)

    @field_validator("Year")
    @classmethod
    def validate_year(cls, v):
        year = int(v)
        if year < 2000 or year > 2100:
            raise ValueError("Invalid year")
        return str(year)


class NilReturnRequest(BaseModel):
    TAXPAYERDETAILS: TaxpayerDetails


class ResponseStatus(str, Enum):
    OK = "OK"
    NOK = "NOK"


class APIResponse(BaseModel):
    ResponseCode: str
    Message: str
    Status: ResponseStatus
    AckNumber: Optional[str] = None


class NilReturnResponse(BaseModel):
    RESPONSE: APIResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None