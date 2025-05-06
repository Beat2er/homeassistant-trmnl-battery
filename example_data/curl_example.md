# TRMNL API Example for Home Assistant Integration

This example shows how to retrieve your TRMNL device data, which this Home Assistant integration uses to display battery and signal information.

## Get Device List

```bash
curl -X 'GET' \
  'https://usetrmnl.com/api/devices' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key_here'
```

The response will contain information about all your devices including battery voltage and WiFi signal strength (RSSI):
```json
{
  "data": [
    {
      "name": "Kitchen TRMNL",
      "friendly_id": "ABC123",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "battery_voltage": 3.92,
      "rssi": -68
    }
  ]
}
```
This is the data that the Home Assistant integration uses to create sensor entities for your TRMNL devices.
