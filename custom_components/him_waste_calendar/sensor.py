"""Sensor platform for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CATEGORIES, DOMAIN
from .coordinator import WasteCalendarCoordinator


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up sensors based on a config entry."""
    coordinator: WasteCalendarCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WasteCategorySensor(coordinator, category)
        for category in CATEGORIES
    ]
    entities.append(WasteNextSensor(coordinator))

    async_add_entities(entities)


class WasteCategorySensor(CoordinatorEntity[WasteCalendarCoordinator], SensorEntity):
    """Sensor representing the next date for a specific category."""

    def __init__(self, coordinator: WasteCalendarCoordinator, category: str) -> None:
        super().__init__(coordinator)
        self._category = category
        self._attr_name = f"HIM next {category.replace('_', ' ')}"
        self._attr_unique_id = f"{coordinator.property_id}_{category}"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get(self._category, STATE_UNKNOWN)


class WasteNextSensor(CoordinatorEntity[WasteCalendarCoordinator], SensorEntity):
    """Sensor showing the next waste collection of any type."""

    def __init__(self, coordinator: WasteCalendarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "HIM next collection"
        self._attr_unique_id = f"{coordinator.property_id}_next"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.coordinator.data

    @property
    def native_value(self) -> str | None:
        parsed: list[date] = []
        today = date.today()
        for value in self.coordinator.data.values():
            try:
                parsed.append(datetime.strptime(value, "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue
        if not parsed:
            return STATE_UNKNOWN
        future = [d for d in parsed if d >= today]
        if future:
            return min(future).isoformat()
        return min(parsed).isoformat()
