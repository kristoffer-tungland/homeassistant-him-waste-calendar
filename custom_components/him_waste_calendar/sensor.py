"""Sensor platform for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from .const import CATEGORIES, DOMAIN, CATEGORY_ICONS, CATEGORY_NAMES
from .coordinator import WasteCalendarCoordinator
from .entity import WasteCalendarEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up sensors based on a config entry."""
    coordinator: WasteCalendarCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WasteCategorySensor(coordinator, category)
        for category in CATEGORIES
    ]
    entities.append(WasteNextSensor(coordinator))

    async_add_entities(entities)


class WasteCategorySensor(WasteCalendarEntity, SensorEntity):
    """Sensor representing the next date for a specific category."""

    _attr_native_unit_of_measurement = "days"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: WasteCalendarCoordinator, category: str) -> None:
        super().__init__(coordinator)
        self._category = category
        name = CATEGORY_NAMES.get(
            category, category.replace("_", " ").title()
        )
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.property_id}_{category}"
        self._attr_icon = CATEGORY_ICONS.get(category)

    def _get_date(self) -> date | None:
        raw = self.coordinator.data.get(self._category)
        if isinstance(raw, date):
            return raw
        if isinstance(raw, str):
            try:
                return datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        d = self._get_date()
        attrs["date"] = d.isoformat() if d else None
        return attrs

    @property
    def native_value(self) -> int | None:
        d = self._get_date()
        if d:
            return (d - date.today()).days
        return None


class WasteNextSensor(WasteCalendarEntity, SensorEntity):
    """Sensor showing the next waste collection of any type."""

    _attr_native_unit_of_measurement = "days"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: WasteCalendarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Neste tømming"
        self._attr_unique_id = f"{coordinator.property_id}_next"
        self._attr_icon = "mdi:calendar"

    def _next_date(self) -> date | None:
        parsed: list[date] = []
        today = date.today()
        for value in self.coordinator.data.values():
            if isinstance(value, date):
                parsed.append(value)
            elif isinstance(value, str):
                try:
                    parsed.append(datetime.strptime(value, "%Y-%m-%d").date())
                except ValueError:
                    continue
        if not parsed:
            return None
        future = [d for d in parsed if d >= today]
        return min(future or parsed)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        attrs.update(self.coordinator.data)
        nd = self._next_date()
        attrs["date"] = nd.isoformat() if nd else None
        return attrs

    @property
    def native_value(self) -> int | None:
        nd = self._next_date()
        if nd:
            return (nd - date.today()).days
        return None
