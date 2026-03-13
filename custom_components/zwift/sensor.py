"""Zwift sensor platform."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    SIGNAL_ZWIFT_UPDATE,
    ZWIFT_IGNORED_PROFILE_ATTRIBUTES,
)

_LOGGER = logging.getLogger(__name__)


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
        self._state = None
        self._attrs = {}
        self._attr_unique_id = "zwift_{}_{}".format(
            SENSOR_TYPES[self._type]["name"], self._player.player_id
        ).replace(" ", "").lower()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to group entities under a single device."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._player.player_id))},
            name=f"Zwift {self._player.friendly_player_id}",
            manufacturer="Zwift",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"https://www.zwift.com/athlete/{self._player.player_id}",
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return SENSOR_TYPES[self._type].get("name")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attrs

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

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

    def update(self):
        """Get the latest data from the sensor."""
        self._state = getattr(self._player, self._type)
        if self._type == "online":
            p = self._player.player_profile
            self._attrs.update(
                {
                    k: p[k]
                    for k in p
                    if k not in ZWIFT_IGNORED_PROFILE_ATTRIBUTES
                }
            )

    async def async_added_to_hass(self):
        """Register update signal handler."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        async_dispatcher_connect(
            self.hass,
            SIGNAL_ZWIFT_UPDATE.format(player_id=self._player.player_id),
            async_update_state,
        )


class ZwiftBinarySensorEntity(ZwiftSensorEntity, BinarySensorEntity):
    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the device class of the binary sensor."""
        return SENSOR_TYPES[self._type].get("device_class")
