"""Base class Rooster Money entities."""
from __future__ import annotations

import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount
from pyroostermoney.const import MOBILE_APP_VERSION
from pyroostermoney.family_account import FamilyAccount

import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RoosterChildEntity(Entity):
    """Base class for Rooster Money Child Entities."""

    _attr_should_poll = True
    _attr_has_entity_name = True

    def __init__(
        self, account: ChildAccount, session: RoosterMoney, entity_id: str
    ) -> None:
        """Initialize the Rooster Money handler."""
        self._session = session
        self._child: ChildAccount = account
        self._entity_id = entity_id

    async def async_update(self) -> bool:
        """Update the entity data."""
        await self._child.update()
        return True

    @property
    def unique_id(self):
        """Return the uniqueid of the child."""
        return f"roostermoney_{self._child.user_id}_{self._entity_id}"

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"roostermoney_{self._child.user_id}")},
            manufacturer="Rooster Money",
            name=str(self._child.first_name),
            sw_version=MOBILE_APP_VERSION,
            entry_type=dr.DeviceEntryType.SERVICE,
        )


class RoosterFamilyEntity(Entity):
    """Base class for Rooster Family Account Entities."""

    _attr_should_poll = True
    _attr_has_entity_name = True

    def __init__(
        self, account: FamilyAccount, session: RoosterMoney, attr: str
    ) -> None:
        """Initialize the Rooster Money handler."""
        self._session = session
        self._account: FamilyAccount = account
        self._attr = attr

    async def async_update(self) -> bool:
        """Update the entity data."""
        await self._account.update()
        return True

    @property
    def unique_id(self):
        """Return the uniqueid of the entity."""
        return f"roostermoney_{self._account.account_number}_{self._attr}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._account.account_number)},
            manufacturer="Rooster Money",
            name="Family Account",
            sw_version=MOBILE_APP_VERSION,
            entry_type=dr.DeviceEntryType.SERVICE,
        )
