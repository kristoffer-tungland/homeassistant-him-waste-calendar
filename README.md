# HIM Waste Calendar

Custom Home Assistant integration that scrapes HIM's waste calendar website and exposes pickup dates as sensors.

## Installation

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository to HACS as a custom repository.
3. Install the **HIM Waste Calendar** integration from the HACS interface.

## Configuration

Use the configuration flow and enter your property ID when prompted. The integration will create one sensor per waste category and an aggregate sensor showing the next upcoming collection.

All sensors for a property are grouped under a single device in Home Assistant and expose a `last_refresh` attribute indicating when data was last updated.
