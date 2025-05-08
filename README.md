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

1. Go to Settings -> Devices & Services.
2. Click "+ Add Integration".
3. Search for "TRMNL".
4. Enter your **User API Key**. This key is **mandatory**. It is used by this integration to fetch general device information (e.g., battery, RSSI) from the `/api/devices` endpoint using `Authorization: Bearer YOUR_API_KEY` authentication. You can typically generate this User API Key from your TRMNL account page (e.g., `https://usetrmnl.com/account`).
5. Optionally, configure the **API Base URL** if you are using a self-hosted or alternative TRMNL service (e.g., `https://your.trmnl.server.com`). The default is `https://usetrmnl.com`. The integration appends API paths like `/api/devices` and `/api/current_screen` to this base URL.
6. Optionally, provide a **Device Access Token**. This token is **optional but required if you want the "Last Seen" sensor**. It is specifically used to fetch the `current_screen` information (including the `rendered_at` timestamp) from the `/api/current_screen` endpoint, which typically uses `access-token: YOUR_DEVICE_ACCESS_TOKEN` authentication. **Important: According to TRMNL documentation, only devices with the Developer add-on can access their Device Access Token. This feature may require a one-time fee and can be unlocked via your TRMNL account (Devices > Edit page).** If this token is not provided or accessible, the "Last Seen" sensor will not be created.
7. Optionally, configure the **Polling Interval** in seconds. This determines how frequently Home Assistant checks for updates from the TRMNL API. The default is 300 seconds (5 minutes). The minimum allowed interval is 60 seconds (1 minute).

These settings can also be changed later by going to the integration's options (Settings -> Devices & Services -> TRMNL -> Configure).

## Entities

For each TRMNL device, the integration creates the following entities:

- **Battery Voltage**: Shows the current battery voltage in volts.
- **Battery Percentage**: Shows the calculated battery level as a percentage.
- **WiFi Signal Strength**: Shows the WiFi RSSI value in dBm.
- **Last Seen** (Optional): Shows the timestamp of the last successful screen render (`rendered_at`) by the TRMNL server for your account, fetched from the `/api/current_screen` endpoint. This sensor is **only created if you provide the "Device Access Token"** during configuration. It is updated only when the TRMNL API provides a new, non-null `rendered_at` timestamp; if the API returns `null` or the data is unavailable, this sensor will retain the last known valid render time.

All sensors include a `last_updated` attribute that shows when Home Assistant last retrieved data from the TRMNL API.

## Battery Calculation

The integration calculates battery percentage based on the following assumptions:

- 2.75V = 0% (device disconnects at this voltage per documentation)
- 4.2V = 100% (typical fully charged LiPo battery)

## Data Update Frequency

The integration checks for updates from the TRMNL API at a configurable interval.
- **Default Polling Interval**: 5 minutes (300 seconds).
- **Minimum Polling Interval**: 1 minute (60 seconds).
This interval can be set during the initial setup of the integration and can be modified later via the integration's configuration options in Home Assistant (Settings -> Devices & Services -> TRMNL -> Configure).

## Understanding the "Last Seen" Timestamp

The "Last Seen" timestamp reflects when the TRMNL server last rendered a new screen image for your account. It's important to understand the different update cycles involved:

1.  **TRMNL Server Render Interval (X)**: This is how often the TRMNL servers internally generate a new image for display. This interval is determined by TRMNL's backend.
2.  **TRMNL Device Refresh Interval (Y)**: This is how often your physical TRMNL e-ink display contacts the TRMNL servers to fetch the latest image. This is typically configured on the device or through your TRMNL account settings.
3.  **Home Assistant Integration Polling Interval (Z)**: This is how often this Home Assistant integration queries the TRMNL API (both for device status and the `current_screen` information). You configure this in Home Assistant.

Because these three intervals (X, Y, and Z) operate independently and may not align perfectly:
- The TRMNL API endpoint (`/api/current_screen/`) might return `null` for the `rendered_at` field. This can happen if the Home Assistant integration polls at a moment when the TRMNL server hasn't rendered a new screen since the last check, or if the content of the screen hasn't changed.
- This integration is designed to handle this: it will only update the "Last Seen" sensor's value when the API provides a new, non-null `rendered_at` timestamp. If `null` is received, the sensor will continue to show the previously recorded valid "Last Seen" time.

This means the "Last Seen" time indicates the most recent screen generation confirmed by the API, not necessarily the exact moment your Home Assistant polled the API or the exact moment your physical device refreshed.

## Support

If you encounter any issues, please submit them on GitHub: https://github.com/Beat2er/homeassistant-trmnl-battery/issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.
