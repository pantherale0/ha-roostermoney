"""Base class Rooster Money entities."""
from __future__ import annotations

import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount, StandingOrder
from pyroostermoney.const import MOBILE_APP_VERSION
from pyroostermoney.family_account import FamilyAccount

import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.core import ServiceResponse
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RoosterChildEntity(Entity):
    """Base class for Rooster Money Child Entities."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(
        self, account: ChildAccount, session: RoosterMoney, entity_id: str
    ) -> None:
        """Initialize the Rooster Money handler."""
        self._session = session
        self._child: ChildAccount = account
        self._entity_id = entity_id

    @property
    def unique_id(self):
        """Return the uniqueid of the child."""
        return f"roostermoney_{self._child.user_id}_{self._entity_id}"

    @property
    def entity_picture(self) -> str | None:
        return self._child.profile_image

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

    async def async_create_standing_order(self, amount, day, frequency, tag, title):
        """Service to create a standing order."""
        standing_order = StandingOrder(
            amount=amount,
            day=day,
            frequency=frequency,
            active=True,
            tag=tag,
            title=title,
            regular_id=None,
        )
        await self._child.create_standing_order(standing_order)

    async def async_delete_standing_order(self, regular_id: str):
        """Deletes a standing order according to its ID"""
        for regular in self._child.standing_orders:
            if regular.regular_id == regular_id:
                await self._child.delete_standing_order(regular)
                break

    async def async_get_standing_orders(self) -> ServiceResponse:
        """Gets all standing orders."""
        return {
            "regulars": [
                {
                    "amount": regular.amount,
                    "title": regular.title,
                    "id": regular.regular_id,
                    "tag": regular.tag,
                }
                for regular in self._child.standing_orders
            ]
        }


class RoosterFamilyEntity(Entity):
    """Base class for Rooster Family Account Entities."""

    _attr_has_entity_name = True
    _attr_should_poll = True

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
