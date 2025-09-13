# Appliance Cycle

Home Assistant custom integration for detecting and tracking appliance cycles (washing machine, dryer, dishwasher) using a power or energy sensor and an optional door sensor. The integration exposes a running binary sensor and helper sensors with run time, last runtime and finished timestamp, plus a friendly status display.

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

## Provided Entities

* `binary_sensor.<name>_running`
* `sensor.<name>_run_time`
* `sensor.<name>_last_runtime`
* `sensor.<name>_finished_at`
* `sensor.<name>_status`

## Development

This repository follows [semantic versioning](https://semver.org/). Pull requests and issues are welcome!
