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
