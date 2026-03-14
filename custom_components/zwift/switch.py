"""Zwift switch platform."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zwift switches from a config entry."""
    zwift_data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for player_id in zwift_data.players:
        player = zwift_data.players[player_id]
        entities.append(ZwiftPollingSwitch(player, entry))

    async_add_entities(entities)


class ZwiftPollingSwitch(SwitchEntity):
    """Switch to enable or disable Zwift update polling for a player."""

    _attr_has_entity_name = True

    def __init__(self, player, entry):
        self._player = player
        self._entry = entry
        self._attr_unique_id = f"zwift_polling_{player.player_id}"

    @property
    def name(self):
        return "Update Polling"

    @property
    def icon(self):
        return "mdi:update" if self.is_on else "mdi:update-lock"

    @property
    def device_info(self) -> DeviceInfo:
        return self._player.device_info

    @property
    def is_on(self):
        return self._player.polling_enabled

    async def async_turn_on(self, **kwargs):
        self._player.polling_enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._player.polling_enabled = False
        self.async_write_ha_state()
