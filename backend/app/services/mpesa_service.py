import httpx
import asyncio
from typing import Dict, Any, Optional
import json
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class MpesaService:
    """Service for M-Pesa Daraja API integration"""

    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment.lower()

        # Base URLs for different environments
        self.base_urls = {
            "sandbox": "https://sandbox.safaricom.co.ke",
            "production": "https://api.safaricom.co.ke"
        }

        self.base_url = self.base_urls.get(self.environment, self.base_urls["sandbox"])

        # Generate base64 encoded credentials
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()

    async def get_oauth_token(self) -> Optional[str]:
        """Get OAuth access token from M-Pesa"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"

        headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                else:
                    logger.error(f"OAuth token request failed: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error getting OAuth token: {e}")
            return None

    async def register_urls(self, shortcode: str, response_type: str = "Completed",
                           confirmation_url: Optional[str] = None,
                           validation_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Register validation and confirmation URLs with M-Pesa"""

        # Get OAuth token first
        token = await self.get_oauth_token()
        if not token:
            return None

        url = f"{self.base_url}/mpesa/c2b/v1/registerurl"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "ShortCode": shortcode,
            "ResponseType": response_type,
            "CommandID": "RegisterURL"
        }

        # Only include URLs if provided
        if confirmation_url:
            payload["ConfirmationURL"] = confirmation_url
        if validation_url:
            payload["ValidationURL"] = validation_url

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"URL registration failed: {response.status_code} - {response.text}")
                    return response.json() if response.headers.get("content-type", "").startswith("application/json") else None

        except Exception as e:
            logger.error(f"Error registering URLs: {e}")
            return None

    async def simulate_transaction(self, shortcode: str, amount: float,
                                 msisdn: str, bill_ref_number: Optional[str] = None) -> Dict[str, Any]:
        """Simulate an M-Pesa C2B transaction (sandbox only)"""

        if self.environment != "sandbox":
            raise ValueError("Simulation only available in sandbox environment")

        # Get OAuth token first
        token = await self.get_oauth_token()
        if not token:
            raise ValueError("Failed to get OAuth token")

        url = f"{self.base_url}/mpesa/c2b/v1/simulate"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "ShortCode": shortcode,
            "CommandID": "CustomerPayBillOnline",
            "Amount": amount,
            "Msisdn": msisdn,
            "BillRefNumber": bill_ref_number or "TestPayment"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    return response.json()
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                    logger.error(f"Transaction simulation failed: {response.status_code} - {error_data}")
                    return error_data

        except Exception as e:
            logger.error(f"Error simulating transaction: {e}")
            raise ValueError(f"Failed to simulate transaction: {e}")

    async def check_transaction_status(self, checkout_request_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of an STK push transaction"""

        # Get OAuth token first
        token = await self.get_oauth_token()
        if not token:
            return None

        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "CheckoutRequestID": checkout_request_id,
            "CommandID": "TransactionStatusQuery"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Transaction status check failed: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return None
