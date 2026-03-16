import json
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .models import (
    NilReturnRequest,
    NilReturnResponse,
    TaxpayerDetails,
    ObligationCode,
    TokenResponse,
)
from .exceptions import (
    KRAAPIError,
    AuthenticationError,
    ValidationError,
    XMLSyntaxError,
    DataValidationError,
    HashValidationError,
)


logger = logging.getLogger(__name__)


class KRAClient:
    """Client for interacting with KRA (Kenya Revenue Authority) APIs"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://sbx.kra.go.ke",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=2
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_access_token(self) -> str:
        """Get or refresh access token for API authentication"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        logger.info("Fetching new access token")
        
        token_url = f"{self.base_url}/oauth/v1/generate"
        params = {"grant_type": "client_credentials"}
        
        try:
            response = self.session.get(
                token_url,
                params=params,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            token_data = TokenResponse(**response.json())
            self.access_token = token_data.access_token
            
            expires_in = token_data.expires_in or 3600
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info("Successfully obtained access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain access token: {e}")
            raise AuthenticationError(f"Failed to authenticate with KRA API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the KRA API"""
        token = self._get_access_token()
        
        url = f"{self.base_url}{endpoint}"
        default_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        if headers:
            default_headers.update(headers)
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            if e.response.status_code == 401:
                self.access_token = None
                raise AuthenticationError("Authentication failed, invalid credentials")
            elif e.response.status_code in [502, 503, 504]:
                raise KRAAPIError(f"KRA server error ({e.response.status_code}): The server is temporarily unavailable. Please try again later.")
            raise KRAAPIError(f"API request failed: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout occurred: {e}")
            raise KRAAPIError(f"Request timed out after {self.timeout} seconds. The KRA server may be experiencing high load. Please try again later.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error occurred: {e}")
            raise KRAAPIError(f"Network error: {e}")

    def file_nil_return(
        self,
        taxpayer_pin: str,
        obligation_code: str,
        month: str,
        year: str,
    ) -> NilReturnResponse:
        """
        File a NIL return for the specified tax period
        
        Args:
            taxpayer_pin: KRA PIN number (format: A000000000L)
            obligation_code: Type of tax obligation
            month: Month of the return (01-12)
            year: Year of the return (e.g., 2024)
            
        Returns:
            NilReturnResponse containing the filing result
            
        Raises:
            ValidationError: If input data is invalid
            KRAAPIError: If API request fails
        """
        logger.info(f"Filing NIL return for PIN {taxpayer_pin}, {month}/{year}")
        
        try:
            taxpayer_details = TaxpayerDetails(
                TaxpayerPIN=taxpayer_pin,
                ObligationCode=obligation_code,
                Month=month,
                Year=year,
            )
            
            request_data = NilReturnRequest(TAXPAYERDETAILS=taxpayer_details)
            
            response_data = self._make_request(
                method="POST",
                endpoint="/dtd/return/v1/nil",
                data=request_data.dict(),
            )
            
            # Debug: Log raw response to understand API format
            logger.debug(f"Raw API response: {response_data}")
            
            # Handle different response formats
            # Some KRA APIs return the response directly without "RESPONSE" wrapper
            if "RESPONSE" in response_data:
                processed_response = {"RESPONSE": response_data["RESPONSE"]}
            elif "Response" in response_data:
                # Convert camelCase to uppercase
                resp = response_data["Response"]
                processed_response = {
                    "RESPONSE": {
                        "ResponseCode": resp.get("ResponseCode") or resp.get("responseCode"),
                        "Message": resp.get("Message") or resp.get("message"),
                        "Status": resp.get("Status") or resp.get("status", "OK"),
                        "AckNumber": resp.get("AckNumber") or resp.get("ackNumber"),
                    }
                }
            else:
                # Try to construct response from root level fields
                processed_response = {
                    "RESPONSE": {
                        "ResponseCode": response_data.get("ResponseCode") or response_data.get("responseCode") or "82000",
                        "Message": response_data.get("Message") or response_data.get("message") or "Success",
                        "Status": response_data.get("Status") or response_data.get("status", "OK"),
                        "AckNumber": response_data.get("AckNumber") or response_data.get("ackNumber") or response_data.get("RequestId"),
                    }
                }
            
            response = NilReturnResponse(**processed_response)
            
            self._handle_response_errors(response)
            
            logger.info(f"Successfully filed NIL return: {response.RESPONSE.Message}")
            return response
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to file NIL return: {e}")
            raise KRAAPIError(f"Failed to file NIL return: {e}")

    def _handle_response_errors(self, response: NilReturnResponse) -> None:
        """Check response for errors and raise appropriate exceptions"""
        if response.RESPONSE.Status == "NOK":
            error_code = response.RESPONSE.ResponseCode.strip()
            error_message = response.RESPONSE.Message
            
            error_map = {
                "82001": XMLSyntaxError,
                "82002": DataValidationError,
                "82003": HashValidationError,
                "82004": AuthenticationError,
            }
            
            exception_class = error_map.get(error_code, KRAAPIError)
            raise exception_class(f"Error {error_code}: {error_message}")

    def check_connection(self) -> bool:
        """Test connection to KRA API"""
        try:
            self._get_access_token()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False