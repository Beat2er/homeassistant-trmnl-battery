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
MIN_VOLTAGE = 3.0  # Battery disconnects at this voltage
MAX_VOLTAGE = 4.2   # Typical fully charged LiPo voltage

# Approximate (voltage, percent) LiPo discharge curve, interpolated as a fallback when the
# API omits `percent_charged` (mainly OG; Model X has a gas gauge and reports percent_charged).
# See https://help.trmnl.com/en/articles/10556850-device-battery-faq
LIPO_SOC_CURVE = [
    (3.27, 0), (3.61, 5), (3.69, 10), (3.71, 15), (3.73, 20), (3.75, 25),
    (3.77, 30), (3.79, 35), (3.80, 40), (3.82, 45), (3.84, 50), (3.85, 55),
    (3.87, 60), (3.91, 65), (3.95, 70), (3.98, 75), (4.02, 80), (4.08, 85),
    (4.11, 90), (4.15, 95), (4.20, 100),
]
