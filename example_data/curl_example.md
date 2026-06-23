# TRMNL API Example for Home Assistant Integration

This example shows how to retrieve your TRMNL device data, which this Home Assistant integration uses to display battery and signal information.

## Get Device List

```bash
curl -X 'GET' \
  'https://usetrmnl.com/api/devices' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key_here'
```

The response contains information about all your devices, including battery voltage,
battery percentage (`percent_charged`), WiFi signal (`rssi` in dBm and `wifi_strength` as a
percentage), and the last time the device contacted the server (`last_ping_at`):
```json
{
  "data": [
    {
      "id": 12345,
      "name": "Kitchen TRMNL",
      "friendly_id": "ABC123",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "battery_voltage": 3.92,
      "rssi": -68,
      "wifi_band": "2.4",
      "sleep_mode_enabled": false,
      "sleep_start_time": 1320,
      "sleep_end_time": 480,
      "last_ping_at": "2026-06-23T18:55:43.598Z",
      "percent_charged": 76.67,
      "wifi_strength": 72,
      "hardware_last_ping_at": "2026-06-23T18:55:43.598Z"
    }
  ]
}
```
This is the data that the Home Assistant integration uses to create sensor entities for your
TRMNL devices. The **Battery Percentage** sensor uses `percent_charged` when available and
otherwise estimates from `battery_voltage`.
