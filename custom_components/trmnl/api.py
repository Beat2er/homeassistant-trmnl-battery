"""TRMNL API client."""
import logging
import requests

from .const import DEFAULT_API_ENDPOINT # Import default for safety, though endpoint should always be passed

_LOGGER = logging.getLogger(__name__)

class TrmnlApiClient:
    """TRMNL API client."""

    def __init__(self, api_key: str, api_endpoint: str = DEFAULT_API_ENDPOINT):
        """Initialize the API client."""
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def get_devices(self):
        """Get TRMNL devices information."""
        try:
            response = requests.get(self.api_endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL devices from %s: %s", self.api_endpoint, err)
            # Re-raise the exception so the coordinator can handle it
            raise

    def get_current_screen_info(self):
        """Get TRMNL current screen information."""
        # Derive the current_screen endpoint from the base api_endpoint
        # Assuming api_endpoint is like "https://example.com/api/devices"
        # We want "https://example.com/api/current_screen"
        if "/devices" not in self.api_endpoint:
            _LOGGER.error(
                "Cannot derive current_screen_info endpoint from base API endpoint: %s",
                self.api_endpoint
            )
            # Or raise a specific error, or return None, depending on desired handling
            # For now, let's raise an error to make it explicit if setup is wrong.
            raise ValueError(
                "API endpoint does not contain '/devices' and cannot be transformed for current_screen_info."
            )
        
        current_screen_endpoint = self.api_endpoint.replace("/devices", "/current_screen")

        # Use specific headers for this endpoint as per user's curl example
        screen_info_headers = {
            "accept": "application/json",
            "access-token": self.api_key # Assuming self.api_key is the token
        }

        try:
            response = requests.get(current_screen_endpoint, headers=screen_info_headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rendered_at")
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            # Re-raise the exception so the coordinator can handle it
            raise
        except ValueError as err: # Catch JSON decoding errors
            _LOGGER.error("Error decoding JSON from TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            raise
