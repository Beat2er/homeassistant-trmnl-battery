"""Sensor platform for TRMNL integration."""
import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    MIN_VOLTAGE,
    MAX_VOLTAGE,
    LIPO_SOC_CURVE,
    CONF_DEVICE_ACCESS_TOKEN,
)

_LOGGER = logging.getLogger(__name__)

def calculate_battery_percentage(voltage):
    """Estimate battery percentage from voltage via the LiPo curve (fallback for percent_charged)."""
    if voltage <= MIN_VOLTAGE:
        return 0
    if voltage >= MAX_VOLTAGE:
        return 100

    for (low_v, low_pct), (high_v, high_pct) in zip(LIPO_SOC_CURVE, LIPO_SOC_CURVE[1:]):
        if low_v <= voltage <= high_v:
            ratio = (voltage - low_v) / (high_v - low_v)
            return round(low_pct + ratio * (high_pct - low_pct))

    return 0 if voltage < LIPO_SOC_CURVE[0][0] else 100

async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up TRMNL sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create sensors for each device
    entities = []
    for device in coordinator.data:
        entities.append(TrmnlBatterySensor(coordinator, device))
        entities.append(TrmnlBatteryPercentageSensor(coordinator, device))
        entities.append(TrmnlRssiSensor(coordinator, device))
        entities.append(TrmnlLastPingSensor(coordinator, device))
        # The render-based "Last Render" sensor needs the optional Device Access Token.
        if entry.data.get(CONF_DEVICE_ACCESS_TOKEN):
            entities.append(TrmnlLastSeenSensor(coordinator, device))

    async_add_entities(entities)

class TrmnlBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for TRMNL sensors."""

    def __init__(self, coordinator, device):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.device = device
        self._friendly_id = device["friendly_id"]
        self._mac_address = device["mac_address"]
        self._name = device["name"]

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._mac_address)},
            "name": self._name,
            "manufacturer": "TRMNL",
            "model": "e-ink display",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        # Simply use the current time as the last_updated attribute
        return {
            "last_updated": dt_util.utcnow().isoformat()
        }

    def get_device_data(self):
        """Get current device data from coordinator."""
        for device in self.coordinator.data:
            if device["friendly_id"] == self._friendly_id:
                return device
        return None

class TrmnlBatterySensor(TrmnlBaseSensor):
    """Representation of a TRMNL battery voltage sensor."""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._mac_address}_battery"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Battery"

    @property
    def state(self):
        """Return the state of the sensor."""
        device_data = self.get_device_data()
        if device_data:
            return float(device_data["battery_voltage"])
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "V"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "voltage"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:battery"


class TrmnlBatteryPercentageSensor(TrmnlBaseSensor):
    """Representation of a TRMNL battery percentage sensor."""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._mac_address}_battery_percentage"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Battery Percentage"

    @property
    def state(self):
        """Return the state of the sensor."""
        device_data = self.get_device_data()
        if not device_data:
            return None
        # Prefer the device's own state-of-charge estimate (`percent_charged`)
        # returned by the TRMNL API. Deriving the percentage from `battery_voltage`
        # via a linear map is unreliable: LiPo voltage is highly non-linear with
        # charge, and the reported voltage swings outside the 3.0-4.2 V window the
        # linear map assumes (e.g. it reads ~4.7 V while charging), which clamps
        # the result to 100% the moment the device is plugged in.
        percent_charged = device_data.get("percent_charged")
        if percent_charged is not None:
            return round(float(percent_charged))
        # Fall back to the voltage-based estimate if the API omits percent_charged.
        return calculate_battery_percentage(float(device_data["battery_voltage"]))

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "battery"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:battery"


class TrmnlRssiSensor(TrmnlBaseSensor):
    """Representation of a TRMNL RSSI sensor."""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._mac_address}_rssi"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Signal Strength"

    @property
    def state(self):
        """Return the state of the sensor."""
        device_data = self.get_device_data()
        if device_data:
            return device_data["rssi"]
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "dBm"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "signal_strength"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:wifi"


class TrmnlLastSeenSensor(TrmnlBaseSensor):
    """Representation of when the TRMNL server last rendered a new screen image."""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._mac_address}_last_seen"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Last Render"

    @property
    def state(self):
        """Return the state of the sensor."""
        rendered_at_str = self.coordinator.last_rendered_at
        if rendered_at_str:
            try:
                # Attempt to parse the timestamp.
                # TRMNL API's `rendered_at` format is assumed to be ISO 8601.
                # If it's a different format, this parsing might need adjustment.
                # Example from a similar API: "2023-10-26T10:30:00Z"
                parsed_datetime = dt_util.parse_datetime(rendered_at_str)
                if parsed_datetime:
                    # Ensure it's timezone-aware and in UTC for Home Assistant
                    return dt_util.as_utc(parsed_datetime).isoformat()
                else:
                    _LOGGER.warning(
                        "Failed to parse 'rendered_at' timestamp: %s for device %s",
                        rendered_at_str,
                        self._friendly_id
                    )
                    return None # Or handle as an error state if preferred
            except ValueError as e:
                _LOGGER.error(
                    "ValueError parsing 'rendered_at' timestamp '%s' for device %s: %s",
                    rendered_at_str,
                    self._friendly_id,
                    e
                )
                return None
        return None

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "timestamp"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock-outline"


class TrmnlLastPingSensor(TrmnlBaseSensor):
    """When the device last contacted the TRMNL server (from /api/devices, no token needed)."""

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._mac_address}_last_ping"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} Last Seen"

    @property
    def state(self):
        """Return the state of the sensor."""
        device_data = self.get_device_data()
        if not device_data:
            return None
        last_ping = device_data.get("last_ping_at")
        if not last_ping:
            return None
        parsed = dt_util.parse_datetime(last_ping)
        if parsed is None:
            _LOGGER.warning(
                "Failed to parse 'last_ping_at' timestamp '%s' for device %s",
                last_ping, self._friendly_id,
            )
            return None
        return dt_util.as_utc(parsed).isoformat()

    @property
    def extra_state_attributes(self):
        """Return the state attributes, including the hardware ping timestamp."""
        attrs = super().extra_state_attributes
        device_data = self.get_device_data()
        if device_data:
            attrs["hardware_last_ping_at"] = device_data.get("hardware_last_ping_at")
        return attrs

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "timestamp"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:access-point-check"
