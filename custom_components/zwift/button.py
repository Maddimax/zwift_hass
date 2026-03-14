"""Zwift button platform."""

from homeassistant.components.button import ButtonEntity
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
    """Set up Zwift buttons from a config entry."""
    zwift_data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for player_id in zwift_data.players:
        player = zwift_data.players[player_id]
        entities.append(ZwiftUpdateButton(player, zwift_data, entry))

    async_add_entities(entities)


class ZwiftUpdateButton(ButtonEntity):
    """Button to manually trigger a Zwift player data update."""

    _attr_has_entity_name = True
    _attr_translation_key = "update"

    def __init__(self, player, zwift_data, entry):
        self._player = player
        self._zwift_data = zwift_data
        self._entry = entry
        self._attr_unique_id = f"zwift_update_{player.player_id}"

    @property
    def icon(self):
        return "mdi:refresh"

    @property
    def device_info(self) -> DeviceInfo:
        return self._player.device_info

    async def async_press(self) -> None:
        """Trigger a manual update for this player."""
        await self.hass.async_add_executor_job(
            self._zwift_data.update_player, self._player.player_id
        )
