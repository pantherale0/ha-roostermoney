"""Rooster Money update coordinator."""

from datetime import timedelta
import logging
import async_timeout

from homeassistant.core import HomeAssistant
from pyroostermoney import RoosterMoney
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


class RoosterCoordinator(DataUpdateCoordinator):
    """Custom update coordinator."""

    def __init__(self, hass: HomeAssistant, rooster: RoosterMoney) -> None:
        """Init the coordinator."""
        super().__init__(
            hass, _LOGGER, name="Rooster Money", update_interval=timedelta(seconds=60)
        )
        self.rooster = rooster

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            async with async_timeout.timeout(50):
                listening_idx = set(self.async_contexts())
                return await self.rooster.update()
        except Exception as err:
            raise UpdateFailed from err
