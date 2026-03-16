"""The Zwift integration."""

from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import (
    _LOGGER,
    CONF_INCLUDE_SELF,
    CONF_PLAYERS,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    SENSOR_TYPES,
)
from .coordinator import ZwiftPlayerCoordinator
from .zwift_data import ZwiftData

PLATFORMS = ["button", "image", "light", "sensor", "switch"]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_PLAYERS, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
                vol.Optional(CONF_INCLUDE_SELF, default=True): cv.boolean,
                vol.Optional(CONF_NAME, default="Zwift"): cv.string,
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=15
                ): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Zwift component from YAML."""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=config[DOMAIN],
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Zwift from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    # Players and include_self live in options so they can be changed later
    players = entry.options.get(CONF_PLAYERS, entry.data.get(CONF_PLAYERS, []))
    include_self = entry.options.get(CONF_INCLUDE_SELF, entry.data.get(CONF_INCLUDE_SELF, True))
    update_interval_sec = entry.options.get(
        CONF_UPDATE_INTERVAL, entry.data.get(CONF_UPDATE_INTERVAL, 15)
    )
    update_interval = timedelta(seconds=update_interval_sec)

    zwift_data = ZwiftData(update_interval, username, password, players, hass)
    try:
        await zwift_data._connect()
    except Exception:
        _LOGGER.exception("Could not connect to Zwift")
        return False

    if include_self:
        zwift_data.add_tracked_player(zwift_data._profile.get("id"))

    coordinators = {}
    for player_id in zwift_data.players:
        coordinator = ZwiftPlayerCoordinator(hass, zwift_data, player_id)
        await coordinator.async_config_entry_first_refresh()
        coordinators[player_id] = coordinator

    # Import entity classes from platforms
    from .button import ZwiftUpdateButton
    from .image import ZwiftProfileImageEntity
    from .light import ZwiftPowerZoneLight
    from .sensor import (
        ZwiftOnlineSensorEntity,
        ZwiftPowerZoneSensorEntity,
        ZwiftSensorEntity,
        ZwiftSportSensorEntity,
    )
    from .switch import ZwiftPollingSwitch

    sensor_entity_classes = {
        "ZwiftOnlineSensorEntity": ZwiftOnlineSensorEntity,
        "ZwiftPowerZoneSensorEntity": ZwiftPowerZoneSensorEntity,
        "ZwiftSportSensorEntity": ZwiftSportSensorEntity,
    }

    self_player_id = zwift_data._profile.get("id") if zwift_data._profile else None
    entities_by_platform = {p: [] for p in PLATFORMS}

    for player_id, coordinator in coordinators.items():
        player = coordinator.player

        entities_by_platform["button"].append(
            ZwiftUpdateButton(player, coordinator, entry)
        )
        entities_by_platform["image"].append(
            ZwiftProfileImageEntity(coordinator, hass, player, entry)
        )
        entities_by_platform["light"].append(
            ZwiftPowerZoneLight(coordinator, player)
        )
        entities_by_platform["switch"].append(
            ZwiftPollingSwitch(player, coordinator, entry)
        )

        for variable in SENSOR_TYPES:
            if SENSOR_TYPES[variable].get("self_only") and player_id != self_player_id:
                continue
            entity_class = sensor_entity_classes.get(
                SENSOR_TYPES[variable].get("entity_class"), ZwiftSensorEntity
            )
            entities_by_platform["sensor"].append(
                entity_class(coordinator, player, variable, entry)
            )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "zwift_data": zwift_data,
        "coordinators": coordinators,
        "entities": entities_by_platform,
    }

    # Remove devices for players that are no longer tracked
    current_player_ids = {(DOMAIN, str(pid)) for pid in zwift_data.players}
    device_registry = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id):
        if not device.identifiers & current_player_ids:
            device_registry.async_remove_device(device.id)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
