"""Calendar platform for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent

from .const import CATEGORY_NAMES, DOMAIN
from .coordinator import WasteCalendarCoordinator
from .entity import WasteCalendarEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up calendar entities from a config entry."""
    coordinator: WasteCalendarCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WasteCollectionCalendar(coordinator)])


class WasteCollectionCalendar(WasteCalendarEntity, CalendarEntity):
    """Calendar entity representing all waste collection days."""

    def __init__(self, coordinator: WasteCalendarCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Avfallstømming"
        self._attr_unique_id = f"{coordinator.property_id}_collection_calendar"
        self._attr_icon = "mdi:trash-can-clock"

    def _events_by_date(self) -> dict[date, list[str]]:
        events: dict[date, list[str]] = {}
        for category, raw in self.coordinator.data.items():
            d: date | None = None
            if isinstance(raw, date):
                d = raw
            elif isinstance(raw, str):
                try:
                    d = datetime.strptime(raw, "%Y-%m-%d").date()
                except ValueError:
                    d = None
            if d is None:
                continue
            events.setdefault(d, []).append(category)
        return events

    def _next_event(self) -> tuple[date, list[str]] | None:
        events = self._events_by_date()
        if not events:
            return None
        d = min(events)
        return d, events[d]

    def _build_event(self, d: date, cats: list[str]) -> CalendarEvent:
        start = d
        end = d + timedelta(days=1)
        desc = ", ".join(
            CATEGORY_NAMES.get(c, c.replace("_", " ").title()) for c in cats
        )
        return CalendarEvent(
            summary=self._attr_name,
            start=start,
            end=end,
            description=desc,
        )

    @property
    def event(self) -> CalendarEvent | None:
        nxt = self._next_event()
        if not nxt:
            return None
        d, cats = nxt
        return self._build_event(d, cats)

    async def async_get_events(
        self, hass, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        events = []
        for d, cats in self._events_by_date().items():
            if d < end_date.date() and d >= start_date.date():
                events.append(self._build_event(d, cats))
        return events

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        attrs = super().extra_state_attributes
        nxt = self._next_event()
        if nxt:
            _d, cats = nxt
            attrs["categories"] = [
                CATEGORY_NAMES.get(c, c.replace("_", " ").title()) for c in cats
            ]
        else:
            attrs["categories"] = []
        return attrs
