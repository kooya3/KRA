class KRAAPIError(Exception):
    """Base exception for KRA API errors"""
    pass


class AuthenticationError(KRAAPIError):
    """Raised when authentication fails"""
    pass


class ValidationError(KRAAPIError):
    """Raised when input validation fails"""
    pass


class XMLSyntaxError(KRAAPIError):
    """Raised when XML syntax error occurs (Error code: 82001)"""
    pass


class DataValidationError(KRAAPIError):
    """Raised when data validation error occurs (Error code: 82002)"""
    pass


class HashValidationError(KRAAPIError):
    """Raised when hash validation fails (Error code: 82003)"""
    pass