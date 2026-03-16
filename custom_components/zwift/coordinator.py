"""Zwift per-player data update coordinator."""

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import _LOGGER, DOMAIN


class ZwiftPlayerCoordinator(DataUpdateCoordinator):
    """Coordinator for a single Zwift player's data updates."""

    def __init__(self, hass, zwift_data, player_id):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{player_id}",
            update_interval=zwift_data.update_interval,
        )
        self.zwift_data = zwift_data
        self.player_id = player_id

    @property
    def player(self):
        """Return the ZwiftPlayerData for this coordinator's player."""
        return self.zwift_data.players[self.player_id]

    async def _async_update_data(self):
        """Fetch data from Zwift for this player."""
        if self.zwift_data._client is None:
            await self.zwift_data._connect()

        await self.zwift_data.update_player(self.player_id)

        player = self.player

        # Handle device name changes
        if player._device_name_changed:
            player._device_name_changed = False
            device_registry = dr.async_get(self.hass)
            device = device_registry.async_get_device(
                identifiers={(DOMAIN, str(self.player_id))}
            )
            if device:
                device_registry.async_update_device(
                    device.id, name=player._last_device_name
                )

        # Adjust polling interval based on online status
        # (only when polling is enabled — update_interval=None means disabled)
        if self.update_interval is not None:
            if player.online:
                self.update_interval = self.zwift_data.online_update_interval
            else:
                self.update_interval = self.zwift_data.update_interval

        return player
