"""Sensor platform for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CATEGORIES, DOMAIN, CATEGORY_ICONS
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


class WasteCalendarEntity(CoordinatorEntity[WasteCalendarCoordinator]):
    """Base class for HIM Waste Calendar entities."""

    def __init__(self, coordinator: WasteCalendarCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.property_id)},
            name=f"HIM Waste Calendar {coordinator.property_id}",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return default attributes for all sensors."""
        last = getattr(self.coordinator, "last_refresh", None)
        return {"last_refresh": last.isoformat() if last else None}


class WasteCategorySensor(WasteCalendarEntity, SensorEntity):
    """Sensor representing the next date for a specific category."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: WasteCalendarCoordinator, category: str) -> None:
        super().__init__(coordinator)
        self._category = category
        self._attr_name = f"HIM next {category.replace('_', ' ')}"
        self._attr_unique_id = f"{coordinator.property_id}_{category}"
        self._attr_icon = CATEGORY_ICONS.get(category)

    @property
    def native_value(self) -> date | None:
        raw = self.coordinator.data.get(self._category)
        if isinstance(raw, date):
            return raw
        if isinstance(raw, str):
            try:
                return datetime.strptime(raw, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None


class WasteNextSensor(WasteCalendarEntity, SensorEntity):
    """Sensor showing the next waste collection of any type."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: WasteCalendarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "HIM next collection"
        self._attr_unique_id = f"{coordinator.property_id}_next"
        self._attr_icon = "mdi:calendar"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        attrs.update(self.coordinator.data)
        return attrs

    @property
    def native_value(self) -> date | None:
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
