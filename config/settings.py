import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Application configuration settings"""
    
    # KRA API Settings
    KRA_CLIENT_ID: str = os.getenv("KRA_CLIENT_ID", "")
    KRA_CLIENT_SECRET: str = os.getenv("KRA_CLIENT_SECRET", "")
    KRA_BASE_URL: str = os.getenv("KRA_BASE_URL", "https://sbx.kra.go.ke")
    
    # Default Values
    DEFAULT_TAXPAYER_PIN: str = os.getenv("DEFAULT_TAXPAYER_PIN", "")
    DEFAULT_OBLIGATION_CODE: str = os.getenv("DEFAULT_OBLIGATION_CODE", "7")
    DEFAULT_MONTH: str = os.getenv("DEFAULT_MONTH", "")
    DEFAULT_YEAR: str = os.getenv("DEFAULT_YEAR", "")
    
    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present"""
        if not cls.KRA_CLIENT_ID:
            raise ValueError("KRA_CLIENT_ID is not set")
        if not cls.KRA_CLIENT_SECRET:
            raise ValueError("KRA_CLIENT_SECRET is not set")
        return True
    
    @classmethod
    def get_obligation_codes(cls) -> dict:
        """Get mapping of obligation codes"""
        return {
            "4": "Income Tax - Company",
            "6": "Income Tax - Withholding",
            "7": "Income Tax - PAYE",
            "9": "Value Added Tax (VAT)",
        }


settings = Settings()