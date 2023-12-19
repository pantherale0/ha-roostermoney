"""Base class Rooster Money entities."""
from __future__ import annotations

import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount, StandingOrder
from pyroostermoney.const import MOBILE_APP_VERSION
from pyroostermoney.family_account import FamilyAccount
from pyroostermoney.enum import JobActions

import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import ServiceResponse
from .const import DOMAIN
from .update_coordinator import RoosterCoordinator

_LOGGER = logging.getLogger(__name__)


class RoosterChildEntity(CoordinatorEntity, Entity):
    """Base class for Rooster Money Child Entities."""

    def __init__(
        self, coordinator: RoosterCoordinator, idx, child_id: int, entity_id: str
    ) -> None:
        """Initialize the Rooster Money handler."""
        super().__init__(coordinator, idx)
        self.idx = idx
        self._child_id = child_id
        self._entity_id = entity_id
        self.coordinator: RoosterCoordinator = coordinator

    @property
    def _child(self) -> ChildAccount:
        """Returns the child data."""
        return self.coordinator.rooster.get_child_account(self._child_id)

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
        await self.coordinator.async_refresh_request()

    async def async_delete_standing_order(self, regular_id: str):
        """Delete a standing order."""
        for regular in self._child.standing_orders:
            if regular.regular_id == regular_id:
                await self._child.delete_standing_order(regular)
                await self.coordinator.async_refresh_request()
                break

    async def async_get_standing_orders(self) -> ServiceResponse:
        """Get all standing orders."""
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

    async def async_update_allowance(self, amount: float, active: bool):
        """Update the child allowance."""
        await self._child.update_allowance(not active, amount)

    async def async_perform_action_on_job(self, action: str, job_id: int):
        """Perform an action on a job."""
        action = action.upper()
        filtered = list(
            filter(lambda job: job.scheduled_job_id == job_id, self._child.jobs)
        )
        if len(filtered) == 1:
            if action == "APPROVE":
                await filtered[0].job_action(JobActions.APPROVE, "")
            else:
                raise ValueError("Invalid or not implemented action")
        else:
            raise ValueError("Invalid job_id")
        await self.coordinator.async_request_refresh()
        return True


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
