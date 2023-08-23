"""Switch platform for rooster money."""

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
import logging
from pyroostermoney import RoosterMoney

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType, UndefinedType

from .const import (
    DOMAIN,
    FAMILY_ACCOUNT_ATTR_MAP,
    CHILD_ACCOUNT_ATTR_MAP,
    ENTITY_SERVICES,
)
from .rooster_base import RoosterChildEntity, RoosterFamilyEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Rooster Money session."""
    entities = []
    for child in hass.data[DOMAIN][config_entry.entry_id].rooster.children:
        entities.append(
            RoosterCardEntity(
                coordinator=hass.data[DOMAIN][config_entry.entry_id],
                idx=None,
                child_id=child.user_id,
                entity_id="card",
            )
        )

    async_add_entities(entities, True)


class RoosterCardEntity(RoosterChildEntity, SwitchEntity):
    """A card switch that enables or disables a card."""

    @property
    def name(self) -> str:
        return "Card"

    @property
    def is_on(self) -> bool:
        return self._child.card.status == "active"

    @property
    def device_class(self) -> SwitchDeviceClass | None:
        return SwitchDeviceClass.SWITCH

    @property
    def device_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "total_spend": self._child.card.total_spend,
            "new_transaction_requires_pin": self._child.card.contactless_count
            == self._child.card.contactless_limit,
            "spend_limit": self._child.card.spend_limit,
        }

    @property
    def entity_picture(self) -> str | None:
        return self._child.card.image
