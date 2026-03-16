"""Zwift switch platform."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zwift switches from a config entry."""
    async_add_entities(hass.data[DOMAIN][entry.entry_id]["entities"]["switch"])


class ZwiftPollingSwitch(SwitchEntity, RestoreEntity):
    """Switch to enable or disable Zwift update polling for a player."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "enable_polling"

    def __init__(self, player, coordinator, entry):
        self._player = player
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"zwift_polling_{player.player_id}"

    async def async_added_to_hass(self):
        """Restore last known state on startup."""
        last_state = await self.async_get_last_state()
        if last_state and last_state.state == "off":
            self._coordinator.update_interval = None

    @property
    def icon(self):
        return "mdi:update" if self.is_on else "mdi:cancel"

    @property
    def device_info(self) -> DeviceInfo:
        return self._player.device_info

    @property
    def is_on(self):
        return self._coordinator.update_interval is not None

    async def async_turn_on(self, **kwargs):
        self._coordinator.update_interval = self._coordinator.zwift_data.update_interval
        await self._coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._coordinator.update_interval = None
        self.async_write_ha_state()
