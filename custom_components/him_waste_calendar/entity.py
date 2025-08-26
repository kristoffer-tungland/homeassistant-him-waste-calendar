"""Shared entity base for HIM Waste Calendar."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class WasteCalendarEntity(CoordinatorEntity):
    """Base entity class for HIM Waste Calendar."""

    def __init__(self, coordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.property_id)},
            name="HIM Tømmekalender",
        )

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return default attributes for entities."""
        last = getattr(self.coordinator, "last_refresh", None)
        return {"last_refresh": last.isoformat() if last else None}
