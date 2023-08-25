"""The Natwest Rooster Money integration."""
from __future__ import annotations

import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.child import StandingOrder
from pyroostermoney.exceptions import InvalidAuthError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError

from .const import DOMAIN
from .update_coordinator import RoosterCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Natwest Rooster Money from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    try:
        rooster = await RoosterMoney.create(
            username=entry.data["username"],
            password=entry.data["password"],
            remove_card_information=entry.data.get("exclude_card_pin", True),
        )

        hass.data[DOMAIN][entry.entry_id] = RoosterCoordinator(hass, rooster)

        # Fetch initial data
        await hass.data[DOMAIN][entry.entry_id].async_config_entry_first_refresh()
    except InvalidAuthError:
        raise ConfigEntryAuthFailed
    except:
        raise CannotConnect

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
