"""Sensors for rooster money."""
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount
from pyroostermoney.family_account import FamilyAccount

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAMILY_ACCOUNT_ATTR_MAP
from .rooster_base import RoosterChildEntity, RoosterFamilyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Rooster Money session."""
    domain_data: RoosterMoney = hass.data[DOMAIN][config_entry.entry_id]
    # Get a list of all children in account
    children = await domain_data.get_children()
    entities = []
    for child in children:
        entities.append(
            RoosterChildPocketMoneySensor(child, domain_data, "pocket_money")
        )
        entities.append(RoosterChildLastTransactionSensor(child, domain_data))

    # Create the family account entities
    family_account = await domain_data.get_family_account()
    for attr in FAMILY_ACCOUNT_ATTR_MAP:
        entities.append(RoosterFamilySensor(family_account, domain_data, attr))

    async_add_entities(entities, True)


class RoosterChildLastTransactionSensor(RoosterChildEntity, SensorEntity):
    """A sensor for Rooster Money."""

    def __init__(self, account: ChildAccount, session: RoosterMoney) -> None:
        super().__init__(account, session, "last_transaction")
        self.transaction = {}

    async def async_update(self) -> None:
        await super().async_update()
        self.transaction = await self._child.get_spend_history(1)
        self.transaction = self.transaction[0]

    @property
    def name(self) -> str:
        return f"{self._child.first_name} Last Transaction"

    @property
    def native_value(self) -> Decimal:
        """Returns the native value of the entity."""
        return self.transaction.get("amount", "Unknown")

    @property
    def native_unit_of_measurement(self) -> str:
        """Returns the unit of measurement for this sensor."""
        return str(self._child.currency).upper()

    @property
    def suggested_display_precision(self) -> int:
        """Returns the display precision (2 decimal places)."""
        return 2

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "description": self.transaction.get("description", "Unknown"),
            "extra_description": self.transaction.get(
                "descriptionExtension", "Unknown"
            ),
            "type": self.transaction.get("type", "Unknown"),
            "balance": self.transaction.get("balance", "Unknown"),
        }


class RoosterChildPocketMoneySensor(RoosterChildEntity, SensorEntity):
    """A sensor for Rooster Money."""

    @property
    def name(self) -> str:
        return f"{self._child.first_name} Available Pocket Money"

    @property
    def native_value(self) -> Decimal:
        """Returns the native value of the entity."""
        return self._child.available_pocket_money

    @property
    def native_unit_of_measurement(self) -> str:
        """Returns the unit of measurement for this sensor."""
        return str(self._child.currency).upper()

    @property
    def suggested_display_precision(self) -> int:
        """Returns the display precision (2 decimal places)."""
        return 2


class RoosterFamilySensor(RoosterFamilyEntity, SensorEntity):
    """A sensor for Rooster Money."""

    def __init__(
        self, account: FamilyAccount, session: RoosterMoney, attr: str
    ) -> None:
        super().__init__(account, session, attr)
        self._name = FAMILY_ACCOUNT_ATTR_MAP.get(attr)

    @property
    def native_value(self) -> object:
        """Returns the native value of the entity."""
        return self._account.__dict__[self._attr]

    @property
    def name(self) -> str:
        return f"Family Account {self._name}"
