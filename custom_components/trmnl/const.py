"""Constants for the TRMNL integration."""

DOMAIN = "trmnl"
SCAN_INTERVAL = 300  # Default scan interval in seconds (5 minutes)

# API
API_ENDPOINT = "https://usetrmnl.com/api/devices"

# Battery voltage limits
MIN_VOLTAGE = 2.75  # Battery disconnects at this voltage
MAX_VOLTAGE = 4.2   # Typical fully charged LiPo voltage