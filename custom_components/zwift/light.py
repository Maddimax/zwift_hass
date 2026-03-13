"""Zwift light platform — power zone color indicator."""

import logging

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ZWIFT_UPDATE

_LOGGER = logging.getLogger(__name__)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zwift power zone light entities."""
    zwift_data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for player_id in zwift_data.players:
        player = zwift_data.players[player_id]
        entities.append(ZwiftPowerZoneLight(player))

    async_add_entities(entities, True)


class ZwiftPowerZoneLight(LightEntity):
    """Light entity representing the current power zone color."""

    _attr_has_entity_name = True
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_icon = "mdi:flash"

    def __init__(self, player):
        self._player = player
        self._attr_unique_id = f"zwift_powerzonecolor_{player.player_id}"

    @property
    def device_info(self):
        return self._player.device_info

    @property
    def name(self):
        return "Power Zone Color"

    @property
    def is_on(self):
        return self._player.power_zone is not None

    @property
    def brightness(self):
        return 255 if self.is_on else 0

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        info = self._player.power_zone
        if info:
            return hex_to_rgb(info[2])
        return None

    async def async_added_to_hass(self):
        """Register update signal handler."""

        async def async_update_state():
            self.async_write_ha_state()

        async_dispatcher_connect(
            self.hass,
            SIGNAL_ZWIFT_UPDATE.format(player_id=self._player.player_id),
            async_update_state,
        )
