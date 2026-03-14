"""Zwift sensor platform."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import MATCH_ALL

from .const import (
    _LOGGER,
    DOMAIN,
    POWER_ZONE_OPTIONS,
    SENSOR_TYPES,
    SIGNAL_ZWIFT_UPDATE,
    ZWIFT_IGNORED_PROFILE_ATTRIBUTES,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zwift sensors from a config entry."""
    zwift_data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for player_id in zwift_data.players:
        player = zwift_data.players[player_id]
        for variable in SENSOR_TYPES:
            if SENSOR_TYPES[variable].get("binary"):
                entities.append(
                    ZwiftBinarySensorEntity(zwift_data, player, variable, entry)
                )
            else:
                entities.append(
                    ZwiftSensorEntity(zwift_data, player, variable, entry)
                )

    async_add_entities(entities, True)


class ZwiftSensorEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, zwift_data, player, sensor_type, entry):
        """Initialize the sensor."""
        self._zwift_data = zwift_data
        self._player = player
        self._type = sensor_type
        self._entry = entry
        if SENSOR_TYPES[self._type].get("translation_key"):
            self._attr_translation_key = SENSOR_TYPES[self._type]["translation_key"]
            self._attr_options = POWER_ZONE_OPTIONS
            self._attr_device_class = "enum"
        self._attr_unique_id = "zwift_{}_{}".format(
            SENSOR_TYPES[self._type]["name"], self._player.player_id
        ).replace(" ", "").lower()

    @property
    def device_info(self):
        return self._player.device_info

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_TYPES[self._type].get("name")

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
    def state(self):
        """Return the state of the sensor."""
        return getattr(self._player, self._type)

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        if self._zwift_data.is_metric:
            return SENSOR_TYPES[self._type].get("unit_metric") or SENSOR_TYPES[
                self._type
            ].get("unit")
        return SENSOR_TYPES[self._type].get("unit")

    @property
    def icon(self):
        return SENSOR_TYPES[self._type].get("icon")

    async def async_added_to_hass(self):
        """Register update signal handler."""

        async def async_update_state():
            """Update sensor state."""
            self.async_write_ha_state()

        async_dispatcher_connect(
            self.hass,
            SIGNAL_ZWIFT_UPDATE.format(player_id=self._player.player_id),
            async_update_state,
        )

class ZwiftBinarySensorEntity(ZwiftSensorEntity, BinarySensorEntity):
    _unrecorded_attributes = frozenset({MATCH_ALL})

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the device class of the binary sensor."""
        return SENSOR_TYPES[self._type].get("device_class")
