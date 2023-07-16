"""The Natwest Rooster Money integration."""
from __future__ import annotations

import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.exceptions import InvalidAuthError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Natwest Rooster Money from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = RoosterMoney(
        entry.data["username"], entry.data["password"]
    )
    try:
        await hass.data[DOMAIN][entry.entry_id].async_login()
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


# class RoosterMoneyCoordinator(DataUpdateCoordinator):
#     """The Rooster Money coordinator."""

#     def __init__(self, hass: HomeAssistant, api: RoosterMoney) -> None:
#         super().__init__(
#             hass, _LOGGER, name="rooster_money", update_interval=timedelta(seconds=30)
#         )

#         self.api = api

#     async def _async_update_data(self) -> Coroutine[Any, Any, Any]:
#         """Fetch data from the API."""
#         try:
#             async with async_timeout.timeout(10):
#                 return await self.api.request_update()
#         except CannotConnect as err:
#             raise ConfigEntryAuthFailed from err
#         except Exception as err:
#             raise UpdateFailed(f"Error communicating with api {err}")


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
