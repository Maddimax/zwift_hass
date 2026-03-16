"""Zwift sensor platform."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    _LOGGER,
    DOMAIN,
    POWER_ZONE_OPTIONS,
    SENSOR_TYPES,
    SPORT_OPTIONS,
    ZWIFT_IGNORED_PROFILE_ATTRIBUTES,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zwift sensors from a config entry."""
    async_add_entities(hass.data[DOMAIN][entry.entry_id]["entities"]["sensor"], True)


class ZwiftSensorEntity(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, player, sensor_type, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._player = player
        self._type = sensor_type
        self._sensor_config = SENSOR_TYPES[sensor_type]
        self._entry = entry
        self._attr_unique_id = "zwift_{}_{}".format(
            self._sensor_config["name"], self._player.player_id
        ).replace(" ", "").lower()

    @property
    def device_info(self):
        return self._player.device_info

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._sensor_config.get("name")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return getattr(self._player, self._type)

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._sensor_config.get("unit")

    @property
    def suggested_unit_of_measurement(self):
        """Return suggested unit based on player's metric preference."""
        use_metric = self._player.player_profile.get("useMetric", True)
        if use_metric:
            return self._sensor_config.get("suggested_unit_metric")
        return self._sensor_config.get("suggested_unit_imperial")

    @property
    def icon(self):
        return self._sensor_config.get("icon")

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._sensor_config.get("device_class")

    @property
    def entity_category(self):
        """Return the entity category."""
        category = self._sensor_config.get("entity_category")
        if category:
            return EntityCategory(category)
        return None

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._sensor_config.get("state_class")


class ZwiftPowerZoneSensorEntity(ZwiftSensorEntity):
    _attr_translation_key = "powerzonename"
    _attr_options = POWER_ZONE_OPTIONS
    _attr_device_class = SensorDeviceClass.ENUM

class ZwiftSportSensorEntity(ZwiftSensorEntity):
    _attr_translation_key = "sport"
    _attr_options = SPORT_OPTIONS
    _attr_device_class = SensorDeviceClass.ENUM

    @property
    def icon(self):
        if self.native_value == "running":
            return "mdi:run"
        return "mdi:bike"

class ZwiftOnlineSensorEntity(ZwiftSensorEntity, BinarySensorEntity):
    _unrecorded_attributes = frozenset({MATCH_ALL})

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self._type != "online":
            return None
        p = self._player.player_profile
        return {
            k: p[k]
            for k in p
            if k not in ZWIFT_IGNORED_PROFILE_ATTRIBUTES
        }

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._player.online
