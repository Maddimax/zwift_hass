"""The Zwift integration."""

import logging
import sys
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import (
    CONF_INCLUDE_SELF,
    CONF_PLAYERS,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    EVENT_ZWIFT_RIDE_ON,
    SIGNAL_ZWIFT_UPDATE,
    ZWIFT_WORLDS,
)

# Patch zwift protobuf
from .zwift_patch import zwift_messages_pb2 as new_pb2

sys.modules["zwift.zwift_messages_pb2"] = new_pb2

from zwift import Client as ZwiftClient
from zwift.error import RequestException

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

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
    players = entry.data.get(CONF_PLAYERS, [])
    include_self = entry.data.get(CONF_INCLUDE_SELF, True)
    update_interval_sec = entry.data.get(CONF_UPDATE_INTERVAL, 15)
    update_interval = timedelta(seconds=update_interval_sec)

    zwift_data = ZwiftData(update_interval, username, password, players, hass)
    try:
        await zwift_data._connect()
    except Exception:
        _LOGGER.exception("Could not connect to Zwift")
        return False

    if include_self:
        zwift_data.add_tracked_player(zwift_data._profile.get("id"))

    async def update_data(now):
        if zwift_data._client is None:
            await zwift_data._connect()
        await hass.async_add_executor_job(zwift_data.update)

        next_update = zwift_data.update_interval
        if zwift_data.any_players_online:
            next_update = zwift_data.online_update_interval

        async_call_later(hass, next_update.total_seconds(), update_data)

    await update_data(None)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = zwift_data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class ZwiftPlayerData:
    def __init__(self, player_id):
        self._player_id = player_id
        self.data = {}
        self.player_profile = {}

    @property
    def player_id(self):
        return self._player_id

    @property
    def friendly_player_id(self):
        return self.player_profile.get("firstName") or self.player_id

    @property
    def online(self):
        return self.data.get("online", False)

    @property
    def hr(self):
        return round(self.data.get("heartrate", 0.0), 0)

    @property
    def speed(self):
        return round(self.data.get("speed", 0.0), 0)

    @property
    def cadence(self):
        return round(self.data.get("cadence", 0.0), 0)

    @property
    def power(self):
        return round(self.data.get("power", 0.0), 0)

    @property
    def altitude(self):
        return round(self.data.get("altitude", 0.0), 1)

    @property
    def distance(self):
        return self.data.get("distance", 0.0)

    @property
    def gradient(self):
        return round(self.data.get("gradient", 0.0), 1)

    @property
    def level(self):
        return self.player_profile.get("playerLevel", None)

    @property
    def runlevel(self):
        return self.player_profile.get("runLevel", None)

    @property
    def cycleprogress(self):
        return self.player_profile.get("cycleProgress", None)

    @property
    def runprogress(self):
        return self.player_profile.get("runProgress", None)


class ZwiftData:
    """Representation of a Zwift client data collection object."""

    def __init__(self, update_interval, username, password, players, hass):
        self._client = None
        self.username = username
        self.password = password
        self.hass = hass
        self.players = {}
        self._profile = None
        self.update_interval = update_interval
        self.online_update_interval = timedelta(seconds=2)
        if players:
            for player_id in players:
                self.add_tracked_player(player_id)

    def add_tracked_player(self, player_id):
        if player_id:
            self.players[player_id] = ZwiftPlayerData(player_id)

    @property
    def any_players_online(self):
        return sum([p.online for p in self.players.values()]) > 0

    async def check_zwift_auth(self, client):
        token = await self.hass.async_add_executor_job(
            client.auth_token.fetch_token_data
        )
        if "error" in token:
            raise Exception("Zwift authorization failed: {}".format(token))
        return True

    @property
    def is_metric(self):
        if self._profile:
            return self._profile.get("useMetric", False)
        return False

    async def _connect(self):
        client = ZwiftClient(self.username, self.password)
        if await self.check_zwift_auth(client):
            self._client = client
            self._profile = await self.hass.async_add_executor_job(
                self._get_self_profile
            )
            return self._client

    def _get_self_profile(self):
        return self._client.get_profile().profile

    def update(self):
        if self._client:
            world = self._client.get_world(1)
            for player_id in self.players:
                data = {}
                online_player = {}
                try:
                    _profile = self._client.get_profile(player_id)
                    player_profile = _profile.profile or {}
                    _LOGGER.debug(
                        "Zwift profile data: {}".format(player_profile)
                    )
                    total_experience = int(
                        player_profile.get("totalExperiencePoints")
                    )
                    player_profile["playerLevel"] = int(
                        player_profile.get("achievementLevel", 0) / 100
                    )
                    player_profile["runLevel"] = int(
                        player_profile.get("runAchievementLevel", 0) / 100
                    )
                    player_profile["cycleProgress"] = int(
                        player_profile.get("achievementLevel", 0) % 100
                    )
                    player_profile["runProgress"] = int(
                        player_profile.get("runAchievementLevel", 0) % 100
                    )
                    latest_activity = _profile.latest_activity
                    latest_activity["world_name"] = ZWIFT_WORLDS.get(
                        latest_activity.get("worldId")
                    )
                    player_profile["latest_activity"] = latest_activity

                    data["total_experience"] = total_experience
                    data["level"] = player_profile["playerLevel"]
                    player_profile["world_name"] = ZWIFT_WORLDS.get(
                        player_profile.get("worldId")
                    )

                    if player_profile.get("riding"):
                        player_state = world.player_status(player_id)
                        _LOGGER.debug(
                            "Zwift player state data: {}".format(
                                player_state.player_state
                            )
                        )
                        altitude = (float(player_state.altitude) - 9000) / 2
                        distance = float(player_state.distance)
                        gradient = self.players[player_id].data.get(
                            "gradient", 0
                        )
                        rideons = latest_activity.get(
                            "activityRideOnCount", 0
                        )
                        if rideons > 0 and rideons > self.players[
                            player_id
                        ].data.get("rideons", 0):
                            self.hass.bus.fire(
                                EVENT_ZWIFT_RIDE_ON,
                                {
                                    "player_id": player_id,
                                    "rideons": rideons,
                                },
                            )
                        if (
                            self.players[player_id].data.get("distance", 0) > 0
                        ):
                            delta_distance = distance - self.players[
                                player_id
                            ].data.get("distance", 0)
                            delta_altitude = altitude - self.players[
                                player_id
                            ].data.get("altitude", 0)
                            if delta_distance > 0:
                                gradient = delta_altitude / delta_distance
                        data.update(
                            {
                                "online": True,
                                "heartrate": int(
                                    float(player_state.heartrate)
                                ),
                                "cadence": int(float(player_state.cadence)),
                                "power": int(float(player_state.power)),
                                "speed": player_state.speed / 1000000.0,
                                "altitude": altitude,
                                "distance": distance,
                                "gradient": gradient,
                                "rideons": rideons,
                            }
                        )
                    online_player.update(player_profile)
                    self.players[player_id].player_profile = online_player
                    self.players[player_id].data = data
                except RequestException as e:
                    if "401" in str(e):
                        self._client = None
                        _LOGGER.warning(
                            "Zwift credentials are wrong or expired"
                        )
                    elif "404" in str(e):
                        _LOGGER.warning(
                            "Upstream Zwift 404 - will try later"
                        )
                    elif "429" in str(e):
                        current_interval = self.online_update_interval
                        new_interval = (
                            self.online_update_interval
                            + timedelta(seconds=0.25)
                        )
                        self.online_update_interval = new_interval
                        _LOGGER.warning(
                            "Upstream request throttling 429 - known issue, "
                            "increasing interval from {}s to {}s".format(
                                current_interval.total_seconds(),
                                new_interval.total_seconds(),
                            )
                        )
                    else:
                        _LOGGER.exception(
                            "something went wrong in Zwift python library - "
                            "{} while updating zwift sensor for player {}".format(
                                str(e), player_id
                            )
                        )
                except Exception:
                    _LOGGER.exception(
                        "something went major wrong while updating zwift "
                        "sensor for player {}".format(player_id)
                    )
                _LOGGER.debug(
                    "dispatching zwift data update for player {}".format(
                        player_id
                    )
                )
                dispatcher_send(
                    self.hass,
                    SIGNAL_ZWIFT_UPDATE.format(player_id=player_id),
                )
