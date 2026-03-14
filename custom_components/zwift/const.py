"""Constants for the Zwift integration."""

import logging

_LOGGER = logging.getLogger('zwift')

DOMAIN = "zwift"

CONF_PLAYERS = "players"
CONF_INCLUDE_SELF = "include_self"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_NAME = "Zwift"

SIGNAL_ZWIFT_UPDATE = "zwift_update_{player_id}"

EVENT_ZWIFT_RIDE_ON = "zwift_ride_on"

ZWIFT_IGNORED_PROFILE_ATTRIBUTES = [
    "privateAttributes",
    "publicAttributes",
    "connectedToStrava",
    "connectedToTrainingPeaks",
    "connectedToTodaysPlan",
    "connectedToUnderArmour",
    "connectedToWithings",
    "connectedToFitbit",
    "connectedToGarmin",
    "connectedToRuntastic",
    "mixpanelDistinctId",
    "bigCommerceId",
    "avantlinkId",
    "userAgent",
    "launchedGameClient",
]

ZWIFT_WORLDS = {
    1: "Watopia",
    2: "Richmond",
    3: "London",
    4: "New York",
    5: "Innsbruck",
    6: "Bologna",
    7: "Yorkshire",
    8: "Crit City",
    9: "Makuri Islands",
    10: "France",
    11: "Paris",
}

SENSOR_TYPES = {
    "online": {"name": "Online", "entity_class": "ZwiftOnlineSensorEntity", "device_class": "connectivity", "icon": "mdi:radio-tower"},
    "hr": {"name": "Heart Rate", "unit": "bpm", "icon": "mdi:heart-pulse"},
    "speed": {"name": "Speed", "unit": "km/h", "device_class": "speed", "suggested_unit_imperial": "mph", "icon": "mdi:speedometer"},
    "cadence": {"name": "Cadence", "unit": "rpm", "icon": "mdi:rotate-right"},
    "power": {"name": "Power", "unit": "W", "device_class": "power", "icon": "mdi:flash"},
    "altitude": {"name": "Altitude", "unit": "cm", "device_class": "distance", "suggested_unit_metric": "m", "suggested_unit_imperial": "ft", "icon": "mdi:altimeter"},
    "distance": {"name": "Distance", "unit": "m", "device_class": "distance", "suggested_unit_metric": "km", "suggested_unit_imperial": "mi", "icon": "mdi:arrow-expand-horizontal"},
    "gradient": {"name": "Gradient", "unit": "°", "state_class": "measurement_angle", "icon": "mdi:image-filter-hdr"},
    "level": {"name": "Level", "icon": "mdi:stairs"},
    "runlevel": {"name": "Run Level", "icon": "mdi:run-fast"},
    "cycleprogress": {"name": "Cycle Progress", "unit": "%", "icon": "mdi:transfer-right"},
    "runprogress": {"name": "Run Progress", "unit": "%", "icon": "mdi:transfer-right"},
    "totaldistance": {"name": "Total Distance", "unit": "m", "device_class": "distance", "suggested_unit_metric": "km", "suggested_unit_imperial": "mi", "icon": "mdi:map-marker-distance"},
    "totaldistanceclimbed": {"name": "Total Distance Climbed", "unit": "m", "device_class": "distance", "suggested_unit_imperial": "ft", "icon": "mdi:elevation-rise"},
    "totaltimeinminutes": {"name": "Total Time", "unit": "min", "device_class": "duration", "suggested_unit_metric": "d", "suggested_unit_imperial": "d", "icon": "mdi:clock-outline"},
    "totalgold": {"name": "Drops", "icon": "mdi:water"},
    "streakscurrentlength": {"name": "Current Streak", "unit": "w", "icon": "mdi:fire"},
    "streaksmaxlength": {"name": "Max Streak", "unit": "w", "icon": "mdi:trophy"},
    "racingscore": {"name": "Racing Score", "icon": "mdi:podium"},
    "racingcategory": {"name": "Racing Category", "icon": "mdi:format-list-numbered"},
    "ftp": {"name": "FTP", "unit": "W", "device_class": "power", "icon": "mdi:flash"},
    "weight": {"name": "Weight", "unit": "g", "device_class": "weight", "suggested_unit_metric": "kg", "suggested_unit_imperial": "lb", "icon": "mdi:weight"},
    "height": {"name": "Height", "unit": "mm", "device_class": "distance", "suggested_unit_metric": "m", "suggested_unit_imperial": "ft", "icon": "mdi:human-male-height"},
    "dob": {"name": "Date of Birth", "device_class": "date", "icon": "mdi:cake-variant"},
    "powerzone": {"name": "Power Zone", "icon": "mdi:gauge"},
    "powerzonename": {"name": "Power Zone Name", "icon": "mdi:gauge", "device_class": "enum", "entity_class": "ZwiftPowerZoneSensorEntity"},
}

POWER_ZONE_OPTIONS = [
    "active_recovery",
    "endurance",
    "tempo",
    "threshold",
    "vo2max",
    "anaerobic",
    "neuromuscular",
]
