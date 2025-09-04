"""HIM Waste Calendar integration."""

from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PROPERTY_ID, DOMAIN, PLATFORMS
from .coordinator import WasteCalendarCoordinator

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HIM Waste Calendar from a config entry."""
    coordinator = WasteCalendarCoordinator(hass, entry.data[CONF_PROPERTY_ID])
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def async_handle_refresh(call):
        await asyncio.gather(
            *[c.async_request_refresh() for c in hass.data.get(DOMAIN, {}).values()]
        )

    if not hass.services.has_service(DOMAIN, "refresh"):
        hass.services.async_register(DOMAIN, "refresh", async_handle_refresh)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "refresh")
    return unload_ok
