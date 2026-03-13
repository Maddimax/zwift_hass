Custom component repository for HACS for the Zwift sensor!

https://community.home-assistant.io/t/zwift-sensor-component-feedback-and-testers-needed/87512


===========

This adds the component to include Zwift sensors in your Home Assistant instance!

Installation
===

1. Install this from HACS
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration** and search for **Zwift Sensor**
4. Enter your Zwift credentials and optionally provide player IDs (comma-separated) to track
5. Your own player will be included automatically unless you uncheck "Include own profile"

Devices & Entities
===

Each tracked player is represented as a **device** in Home Assistant. The device page includes:

* A link to the player's Zwift profile at `zwift.com/athlete/<player_id>`
* A **Profile Picture** image entity

The following **sensor entities** are created per player:

| Entity | Type | Description |
|--------|------|-------------|
| Online | Binary sensor | Whether the player is currently riding |
| Heart Rate | Sensor | Current heart rate (bpm) |
| Speed | Sensor | Current speed (mph / kmh) |
| Cadence | Sensor | Current cadence (rpm) |
| Power | Sensor | Current power (W) |
| Altitude | Sensor | Current altitude (ft / cm) |
| Distance | Sensor | Distance ridden (miles / m) |
| Gradient | Sensor | Current gradient (%) |
| Level | Sensor | Cycling level |
| Run Level | Sensor | Running level |
| Cycle Progress | Sensor | Progress to next cycling level (%) |
| Run Progress | Sensor | Progress to next running level (%) |

Managing Players
===

To add or remove tracked players after initial setup:

1. Go to **Settings → Devices & Services → Zwift Sensor**
2. Click **Configure**
3. Edit the player IDs (comma-separated) and click Submit

The integration will reload automatically and devices for removed players will be cleaned up.

Events
===

This integration will emit the following events:

## `zwift_ride_on`

When an online player receives a "Ride On!" from another player, this event will be emitted with the following data:

```
player_id: <the tracked player id receiving the ride on>
rideons: <the total number of ride ons received on the current ride>
```

### Device Trigger

The `zwift_ride_on` event is also available as a **device trigger** for automations. When creating an automation, select a Zwift player device and choose the **"Ride On received"** trigger.

### Template Access

This information can also be accessed from the `latest_activity` attribute on the Online sensor in a template:

`{{ state_attr('sensor.zwift_online_<playerid>','latest_activity').activityRideOnCount }}`

Attributes
===

The Online sensor is populated with attributes from the Zwift API profile data and latest activity data. Users are encouraged to explore this data and decide what to do with it. Some examples of useful information:

* Number of followers
* Number of ride ons received on last/current ride
* Distance/Wattage/Elevation/Length/Calories/Title/Start&End Date of the last/current activity
* Total all time statistics (watt hours, distance, elevation etc)
* Current FTP
