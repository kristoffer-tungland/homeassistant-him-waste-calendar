"""Data coordinator for the HIM Waste Calendar integration."""

from __future__ import annotations

from datetime import timedelta, date, datetime
import asyncio
import logging

import async_timeout
from bs4 import BeautifulSoup
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import CATEGORIES, DOMAIN, MONTHS

_LOGGER = logging.getLogger(__name__)


class WasteCalendarCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator to fetch waste collection dates."""

    def __init__(self, hass: HomeAssistant, property_id: str) -> None:
        """Initialize the coordinator."""
        self.property_id = property_id
        self.url = f"https://him.as/tommekalender/?eiendomId={property_id}"
        self.last_refresh: datetime | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=6),
        )

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from the source with retry handling."""
        session = async_get_clientsession(self.hass)
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                async with async_timeout.timeout(30):
                    async with session.get(self.url) as response:
                        response.raise_for_status()
                        text = await response.text()

                soup = BeautifulSoup(text, "html.parser")
                categories = soup.select(".tommekalender__next__category")

                if len(categories) < len(CATEGORIES):
                    raise ValueError("Incomplete category data in response")

                data: dict[str, str] = {}
                today = date.today()

                for idx, cat in enumerate(categories[: len(CATEGORIES)]):
                    name = CATEGORIES[idx]
                    date_elem = cat.select_one(".tommekalender__next__date")
                    if date_elem is None:
                        raise ValueError(f"Missing date element for {name}")
                    txt = date_elem.get_text(strip=True).lower()
                    parts = txt.split(".")
                    if len(parts) < 2:
                        raise ValueError(f"Unable to parse date for {name}: {txt}")
                    day = int(parts[0])
                    month_name = parts[-1].strip()
                    month = MONTHS.get(month_name)
                    if not month or day <= 0:
                        raise ValueError(f"Invalid date for {name}: {txt}")
                    year = today.year
                    try_date = date(year, month, day)
                    data[name] = try_date.isoformat()

                self.last_refresh = dt_util.utcnow()
                return data

            except Exception as err:  # broad to catch parsing and network issues
                last_error = err
                _LOGGER.warning(
                    "Attempt %s to fetch waste calendar failed: %s", attempt + 1, err
                )
                await asyncio.sleep(1)

        raise UpdateFailed(
            f"Error fetching waste calendar data: {last_error}"
        ) from last_error
