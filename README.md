# Home Assistant TRMNL Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/yourusername/homeassistant-trmnl)](https://github.com/Beat2er/homeassistant-trmnl-battery/releases)
[![GitHub license](https://img.shields.io/github/license/yourusername/homeassistant-trmnl)](https://github.com/Beat2er/homeassistant-trmnl-battery/blob/main/LICENSE)

This integration allows you to monitor your TRMNL e-ink display devices from Home Assistant, showing battery voltage, battery percentage, and WiFi signal strength.

## Quick Add to HACS

[![Open your Home Assistant instance and add this repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Beat2er&repository=homeassistant-trmnl-battery&category=integration)

## Installation

### Option 1: HACS (recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed
2. Go to HACS -> Integrations
3. Click on the three dots in the top right corner and select "Custom repositories"
4. Add `https://github.com/Beat2er/homeassistant-trmnl-battery` as a custom repository (Category: Integration)
5. Click "Install" on the TRMNL integration
6. Restart Home Assistant

### Option 2: Manual Installation

1. Download the latest release
2. Unpack and copy the `custom_components/trmnl` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings -> Devices & Services
2. Click "+ Add Integration"
3. Search for "TRMNL"
4. Enter your API key (you can find this in your TRMNL account)

## Entities

For each TRMNL device, the integration creates the following entities:

- **Battery Voltage**: Shows the current battery voltage in volts
- **Battery Percentage**: Shows the calculated battery level as a percentage
- **WiFi Signal Strength**: Shows the WiFi RSSI value in dBm
- **Last Seen**: Shows when the device was last seen by the TRMNL server

All sensors include a `last_updated` attribute that shows when Home Assistant last retrieved data from the TRMNL API.

## Battery Calculation

The integration calculates battery percentage based on the following assumptions:

- 2.75V = 0% (device disconnects at this voltage per documentation)
- 4.2V = 100% (typical fully charged LiPo battery)

## Data Update Frequency

By default, the integration checks for updates every 5 minutes. This can be changed in the code if needed.

## Support

If you encounter any issues, please submit them on GitHub: https://github.com/Beat2er/homeassistant-trmnl-battery/issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.
