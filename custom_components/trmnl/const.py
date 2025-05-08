"""Constants for the TRMNL integration."""

DOMAIN = "trmnl"

# Configuration and options
CONF_API_KEY = "api_key"
CONF_API_BASE_URL = "api_base_url" # Renamed from CONF_API_ENDPOINT
CONF_DEVICE_ACCESS_TOKEN = "device_access_token" # New constant
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_API_BASE_URL = "https://usetrmnl.com" # Renamed and updated from DEFAULT_API_ENDPOINT
MIN_SCAN_INTERVAL = 60 # Minimum scan interval in seconds (1 minute)


# Battery voltage limits
MIN_VOLTAGE = 2.75  # Battery disconnects at this voltage
MAX_VOLTAGE = 4.2   # Typical fully charged LiPo voltage
