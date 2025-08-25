"""Constants for the HIM Waste Calendar integration."""

from __future__ import annotations

DOMAIN = "him_waste_calendar"
CONF_PROPERTY_ID = "property_id"
PLATFORMS: list[str] = ["sensor"]

CATEGORIES = [
    "plast",
    "mat",
    "papir",
    "rest",
    "glass_metall",
]

MONTHS = {
    "januar": 1,
    "februar": 2,
    "mars": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "desember": 12,
}
