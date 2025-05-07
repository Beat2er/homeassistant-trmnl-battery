"""Constants for the TRMNL integration."""

DOMAIN = "trmnl"

# Configuration Keys
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_API_ENDPOINT = "api_endpoint"

# Default values
DEFAULT_SCAN_INTERVAL = 300  # Default scan interval in seconds (5 minutes)
DEFAULT_API_ENDPOINT = "https://usetrmnl.com/api/devices"
MIN_SCAN_INTERVAL = 60 # Minimum scan interval in seconds (1 minute)


# Battery voltage limits
MIN_VOLTAGE = 2.75  # Battery disconnects at this voltage
MAX_VOLTAGE = 4.2   # Typical fully charged LiPo voltage
