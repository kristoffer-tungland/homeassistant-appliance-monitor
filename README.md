# Appliance Cycle

Home Assistant custom integration for detecting and tracking appliance cycles (washing machine, dryer, dishwasher) using a power or energy sensor and an optional door sensor. The integration exposes a running binary sensor, helper sensors with run time/last runtime/finished timestamp/energy, plus a friendly status display with extra attributes for dashboards and automations.

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS.
3. Search for **Appliance Cycle** and install.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/appliance_cycle` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

Use the Home Assistant UI to add **Appliance Cycle** from the integration menu. You will be asked for:

* Appliance type (washer, dryer or dishwasher)
* Power or energy sensor entity
* Optional door sensor

Default detection thresholds are applied for each appliance type and can be adjusted later in the integration options.

### Options

All detection thresholds and timings can be tuned from the integration options dialog:

* **Delay on / Delay off / Quiet end / Minimum run / Resume grace** – control how long the integration waits to confirm that an appliance has started or finished.
* **Start grace** – number of seconds that brief dips below the on-threshold are ignored while confirming a start, helping catch appliances that momentarily idle before the cycle fully begins.

## Provided Entities

* `binary_sensor.<name>_running`
* `binary_sensor.<name>_door` (only when a door sensor is configured)
* `sensor.<name>_run_time`
* `sensor.<name>_last_runtime`
* `sensor.<name>_finished_at`
* `sensor.<name>_energy`
* `sensor.<name>_status`

### Status Sensor Attributes

The status sensor exposes extra attributes you can use in templates and Lovelace:

* `run_time` (formatted string like `1h 23m`)
* `run_time_seconds`
* `last_runtime_seconds`
* `started_at`
* `finished_at`
* `door_open`

Status states are `Idle`, `Running`, `Finished`, or `Started` (a brief pre-running confirmation).

## Dashboard Examples

### Show run time while running

Use the status sensor so the entity card displays the running time attribute, and only show it when the appliance is running.

```yaml
type: entity
show_name: true
show_state: true
show_icon: true
entity: sensor.washing_machine_status
icon: mdi:washing-machine
state_content: run_time
visibility:
  - condition: state
    entity: binary_sensor.washing_machine_running
    state: "on"
name:
  type: device
```

### Show how long it has been finished

This card keeps the "Finished" state visible and highlights it.

```yaml
type: tile
entity: sensor.washing_machine_finished_at
features_position: bottom
vertical: false
name: Washing machine finished
state_content: state
icon: mdi:washing-machine
color: red
visibility:
  - condition: state
    entity: sensor.washing_machine_status
    state: Finished
```

## Automation Examples

### Alert when wet laundry sits too long

Trigger a reminder when the status has been `Finished` for a set time. Adjust the `for` value to your preference.

```yaml
alias: Laundry reminder
mode: single
trigger:
  - platform: state
    entity_id: sensor.washing_machine_status
    to: "Finished"
    for: "04:00:00"
condition: []
action:
  - service: notify.mobile_app_phone
    data:
      message: "The laundry has been finished for 4 hours. Time to move it!"
```

If you have a door sensor configured, opening the door clears the finished state so the reminder will reset automatically.

## Development

This repository follows [semantic versioning](https://semver.org/). Pull requests and issues are welcome!

### Releases

* Merges to `main` trigger the stable release workflow, which bumps the patch version and publishes a GitHub release from the latest stable tag.
* Merges to `develop` trigger prereleases with `X.Y.Z-beta.N` tags based on the next stable patch version.
