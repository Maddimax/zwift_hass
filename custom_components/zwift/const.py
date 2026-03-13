"""Constants for the Zwift integration."""

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
    "imageSrc",
    "imageSrcLarge",
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
    "online": {"name": "Online", "binary": True, "device_class": "connectivity", "icon": "mdi:radio-tower"},
    "hr": {"name": "Heart Rate", "unit": "bpm", "icon": "mdi:heart-pulse"},
    "speed": {"name": "Speed", "unit": "mph", "unit_metric": "kmh", "icon": "mdi:speedometer"},
    "cadence": {"name": "Cadence", "unit": "rpm", "icon": "mdi:rotate-right"},
    "power": {"name": "Power", "unit": "W", "icon": "mdi:flash"},
    "altitude": {"name": "Altitude", "unit": "ft", "unit_metric": "cm", "icon": "mdi:altimeter"},
    "distance": {"name": "Distance", "unit": "miles", "unit_metric": "m", "icon": "mdi:arrow-expand-horizontal"},
    "gradient": {"name": "Gradient", "unit": "%", "icon": "mdi:image-filter-hdr"},
    "level": {"name": "Level", "icon": "mdi:stairs"},
    "runlevel": {"name": "Run Level", "icon": "mdi:run-fast"},
    "cycleprogress": {"name": "Cycle Progress", "unit": "%", "icon": "mdi:transfer-right"},
    "runprogress": {"name": "Run Progress", "unit": "%", "icon": "mdi:transfer-right"},
    "totaldistance": {"name": "Total Distance", "unit": "m", "icon": "mdi:map-marker-distance"},
    "totaldistanceclimbed": {"name": "Total Distance Climbed", "unit": "ft", "unit_metric": "m", "icon": "mdi:elevation-rise"},
    "totaltimeinminutes": {"name": "Total Time In Minutes", "unit": "min", "icon": "mdi:clock-outline"},
    "totalgold": {"name": "Drops", "icon": "mdi:water"},
    "streakscurrentlength": {"name": "Current Streak", "unit": "days", "icon": "mdi:fire"},
    "streaksmaxlength": {"name": "Max Streak", "unit": "days", "icon": "mdi:trophy"},
    "racingscore": {"name": "Racing Score", "icon": "mdi:podium"},
    "racingcategory": {"name": "Racing Category", "icon": "mdi:format-list-numbered"},
}
