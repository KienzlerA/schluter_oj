# Schluter DITRA-HEAT-E-WiFi (EU / OJ Electronics) – Home Assistant Integration

This integration provides support for **European Schluter DITRA-HEAT-E-WiFi thermostats**, which are powered by **OJ Electronics (OWD5 platform)**.

⚠️ **Important**

The API used by **European devices is different from the North American Schluter API**.

- 🇺🇸 US devices use the Schluter cloud (`ditra-heat-e-wifi.schluter.com`)
- 🇪🇺 EU devices use the **OJ Electronics backend** (`*.ojelectronics.com`)

Because of this, the official Home Assistant Schluter integration and most existing community integrations do **not work with EU devices**.

This integration reverse-engineers and implements the **OJ Electronics cloud API used by the mobile app**.

The goal is to provide:

- full monitoring of thermostats
- control of heating modes
- schedule awareness
- integration with Home Assistant automations

---

# Supported devices

Tested with:

- **Schluter DITRA-HEAT-E-WiFi (EU models)**
- OJ Electronics **OWD5** platform

These are commonly installed with electric floor heating systems in Europe.

---

# Features

Currently supported:

- Read thermostat status
- Read floor temperature
- Read room temperature
- Read heating state
- Read schedule data
- Read active heating setpoint
- Change heating mode (schedule / comfort / boost / eco)

Planned:

- Full `climate` entity support
- Schedule editing
- Boost duration configuration
- Native thermostat UI

---

# Entities

The integration exposes several entities in Home Assistant.

Entity IDs will depend on the name of your group/thermostats.

## Group entities

These represent the **heating zone / group** (e.g. *Entrance + Kitchen*).

| Entity | Type | Description |
|------|------|-------------|
| `sensor.<group>_active_setpoint` | sensor | Current heating setpoint used by the thermostat |
| `sensor.<group>_mode` | sensor | Current operating mode (`schedule`, `comfort`, `boost`, `eco`) |
| `sensor.<group>_next_setpoint` | sensor | Next scheduled temperature |
| `sensor.<group>_next_event_time` | sensor | Time of the next scheduled change |
| `sensor.<group>_status` | sensor | Human readable status (ex: *Boost active – returns to 16°C in 00:30:00*) |
| `sensor.<group>_boost_countdown` | sensor | Remaining boost time |
| `select.<group>_mode` | select | Allows changing the heating mode |
| `binary_sensor.<group>_show_return_to_schedule` | binary sensor | Indicates whether a "Return to Schedule" button should be shown |

Example:

```
sensor.entrance_kitchen_active_setpoint
sensor.entrance_kitchen_mode
sensor.entrance_kitchen_next_setpoint
sensor.entrance_kitchen_next_event_time
sensor.entrance_kitchen_status
sensor.entrance_kitchen_boost_countdown
select.entrance_kitchen_mode
binary_sensor.entrance_kitchen_show_return_to_schedule
```

---

## Thermostat entities

Each physical thermostat exposes its own sensors.

| Entity | Type | Description |
|------|------|-------------|
| `sensor.<thermostat>_room_temperature` | sensor | Measured room temperature |
| `sensor.<thermostat>_floor_temperature` | sensor | Measured floor temperature |
| `sensor.<thermostat>_comfort_setpoint` | sensor | Comfort setpoint |
| `sensor.<thermostat>_manual_setpoint` | sensor | Manual temperature setpoint |
| `sensor.<thermostat>_regulation_mode` | sensor | Raw regulation mode from API |
| `binary_sensor.<thermostat>_online` | binary sensor | Thermostat connectivity |
| `binary_sensor.<thermostat>_heating` | binary sensor | Heating currently active |
| `binary_sensor.<thermostat>_open_window` | binary sensor | Window open detection |

Example:

```
sensor.kitchen_room_temperature
sensor.kitchen_floor_temperature
binary_sensor.kitchen_heating
```

---

# Heating modes

The integration supports the following operating modes.

| Mode | Description |
|-----|-------------|
| `schedule` | Uses the configured heating schedule |
| `comfort` | Overrides schedule with comfort setpoint |
| `boost` | Temporary heating boost (typically ~40°C floor) |
| `eco` | Reduced temperature (energy saving mode) |

These modes can be controlled via:

```
select.<group>_mode
```

Example service call:

```
service: select.select_option
target:
  entity_id: select.entrance_kitchen_mode
data:
  option: boost
```

---

# Example Lovelace dashboard

Example configuration:

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.entrance_kitchen_active_setpoint
    name: Entrance + Kitchen
    min: 5
    max: 40
    needle: true

  - type: entities
    entities:
      - entity: sensor.entrance_kitchen_mode
        name: Current mode
      - entity: sensor.entrance_kitchen_next_setpoint
        name: Next temperature
      - entity: sensor.entrance_kitchen_next_event_time
        name: Next schedule change

  - type: horizontal-stack
    cards:
      - type: button
        name: Boost
        icon: mdi:rocket-launch
        tap_action:
          action: call-service
          service: select.select_option
          target:
            entity_id: select.entrance_kitchen_mode
          data:
            option: boost

      - type: button
        name: Comfort
        icon: mdi:foot-print
        tap_action:
          action: call-service
          service: select.select_option
          target:
            entity_id: select.entrance_kitchen_mode
          data:
            option: comfort

      - type: button
        name: Eco
        icon: mdi:leaf
        tap_action:
          action: call-service
          service: select.select_option
          target:
            entity_id: select.entrance_kitchen_mode
          data:
            option: eco
```

---

# Smart heating automation

Because the integration exposes both:

- **room temperature**
- **floor temperature**
- **schedule state**

it becomes possible to implement **smart heating logic** in Home Assistant.

Typical examples:

- Reduce floor heating if a **fireplace heats the room**
- Maintain minimal floor warmth for comfort
- Combine floor heating with **heat pump or radiators**
- Build a **house-level thermostat**

Example automation idea:

```
If room temperature > 23°C
→ switch floor heating to comfort mode

If room temperature < 21°C
→ return to schedule
```

---

# Disclaimer

This project is **not affiliated with Schluter or OJ Electronics**.

The API used here has been **reverse engineered from the official mobile application**.

Use at your own risk.