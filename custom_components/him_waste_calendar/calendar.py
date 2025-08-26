"""Calendar platform for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent

from .const import CATEGORY_ICONS, CATEGORY_NAMES, CATEGORIES, DOMAIN
from .coordinator import WasteCalendarCoordinator
from .entity import WasteCalendarEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up calendar entities from a config entry."""
    coordinator: WasteCalendarCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        WasteCalendar(coordinator, category)
        for category in CATEGORIES
    ]
    async_add_entities(entities)


class WasteCalendar(WasteCalendarEntity, CalendarEntity):
    """Calendar entity representing next pickup date for a waste category."""

    def __init__(self, coordinator: WasteCalendarCoordinator, category: str) -> None:
        super().__init__(coordinator)
        self._category = category
        name = CATEGORY_NAMES.get(
            category, category.replace("_", " ").title()
        )
        self._attr_name = f"{name} kalender"
        self._attr_unique_id = f"{coordinator.property_id}_{category}_calendar"
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

    def _build_event(self) -> CalendarEvent | None:
        d = self._get_date()
        if not d:
            return None
        start = d
        end = d + timedelta(days=1)
        return CalendarEvent(summary=self._attr_name, start=start, end=end)

    @property
    def event(self) -> CalendarEvent | None:
        return self._build_event()

    async def async_get_events(
        self, hass, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        ev = self._build_event()
        if ev and ev.start < end_date.date() and ev.end > start_date.date():
            return [ev]
        return []
