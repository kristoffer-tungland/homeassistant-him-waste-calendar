"""Constants for the HIM Waste Calendar integration."""

from __future__ import annotations

DOMAIN = "him_waste_calendar"
CONF_PROPERTY_ID = "property_id"
PLATFORMS: list[str] = ["sensor", "calendar"]

CATEGORIES = [
    "rest",
    "mat",
    "papir",
    "plast",
    "glass_metall",
]

CATEGORY_ICONS = {
    "plast": "mdi:recycle",
    "mat": "mdi:food-apple",
    "papir": "mdi:file-document",
    "rest": "mdi:trash-can",
    "glass_metall": "mdi:bottle-wine",
}

CATEGORY_NAMES = {
    "plast": "Plastavfall",
    "mat": "Matavfall",
    "papir": "Papiravfall",
    "rest": "Restavfall",
    "glass_metall": "Glass og metallavfall",
}

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
