"""Sensors for rooster money."""
from collections.abc import Mapping
from decimal import Decimal
from typing import Any
import logging

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount, Pot
from pyroostermoney.family_account import FamilyAccount

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    domain_data: RoosterMoney = hass.data[DOMAIN][config_entry.entry_id]
    # Get a list of all children in account
    children = domain_data.children
    entities = []
    for child in children:
        entities.append(RoosterChildMoneySensor(child, domain_data, "pocket_money"))
        entities.append(RoosterChildLastTransactionSensor(child, domain_data))
        for pot in child.pots:
            entities.append(RoosterPotSensor(child, domain_data, "pot", pot.pot_id))

    # Create the family account entities
    family_account = domain_data.family_account
    for attr in FAMILY_ACCOUNT_ATTR_MAP:
        entities.append(RoosterFamilySensor(family_account, domain_data, attr))

    async_add_entities(entities, True)
    platform = entity_platform.async_get_current_platform()
    # register services
    for service in ENTITY_SERVICES:
        name = service
        service = ENTITY_SERVICES.get(service)
        schema = service.get("schema")
        function = service.get("function")
        required_features = service.get("required_features", None)
        platform.async_register_entity_service(
            name=name, schema=schema, func=function, required_features=required_features
        )


class RoosterChildLastTransactionSensor(RoosterChildEntity, SensorEntity):
    """A sensor for Rooster Money."""

    def __init__(self, account: ChildAccount, session: RoosterMoney) -> None:
        super().__init__(account, session, "last_transaction")
        self.transaction = account.latest_transaction

    async def async_update(self) -> None:
        await super().async_update()
        self.transaction = self._child.latest_transaction

    @property
    def name(self) -> str:
        return f"Last Transaction"

    @property
    def native_value(self) -> float:
        """Returns the native value of the entity."""
        return self.transaction.amount

    @property
    def native_unit_of_measurement(self) -> str:
        """Returns the unit of measurement for this sensor."""
        return str(self.transaction.currency.upper())

    @property
    def suggested_display_precision(self) -> int:
        """Returns the display precision (2 decimal places)."""
        return 2

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.MONETARY

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "description": self.transaction.description,
            "extra_description": self.transaction.extended_description,
            "type": self.transaction.transaction_type,
            "balance": self.transaction.new_balance,
        }


class RoosterPotSensor(RoosterChildEntity, SensorEntity):
    """A Rooster pot."""

    def __init__(
        self, account: ChildAccount, session: RoosterMoney, entity_id: str, pot: str
    ) -> None:
        self._attr = CHILD_ACCOUNT_ATTR_MAP.get(entity_id)
        self._pot_id = pot
        self._pot = [x for x in account.pots if x.pot_id == pot][0]
        super().__init__(account, session, f"{entity_id}_{pot}")
        self._attr_should_poll = True  # forces the sensor to update

    @property
    def name(self) -> str:
        return str(self._attr.get("name")).format(pot_name=self._pot.name)

    async def async_update(self) -> None:
        _LOGGER.debug("Updating pot %s", self._pot.pot_id)
        self._pot = [x for x in self._child.pots if x.pot_id == self._pot_id][0]

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self._attr.get("native_unit_of_measurement")

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return self._attr.get("device_class")

    @property
    def native_value(self) -> Decimal:
        return self._pot.value

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {"target": self._pot.target, "id": self._pot.pot_id}

    @property
    def entity_picture(self) -> str | None:
        return self._pot.image

    @property
    def enabled(self) -> bool:
        return self._pot.enabled


class RoosterChildMoneySensor(RoosterChildEntity, SensorEntity):
    """A sensor for Rooster Money."""

    @property
    def name(self) -> str:
        return "Available Pocket Money"

    @property
    def native_value(self) -> Decimal:
        """Returns the native value of the entity."""
        return self._child.available_pocket_money

    @property
    def native_unit_of_measurement(self) -> str:
        """Returns the unit of measurement for this sensor."""
        return str(self._child.currency).upper()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.MONETARY

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
        self._attr = attr
        self._attr_config: dict = FAMILY_ACCOUNT_ATTR_MAP.get(attr)
        self._type = self._attr_config.get("type", None)

    @property
    def native_value(self) -> str | float | None:
        """Returns the native value of the entity."""
        if self._type is None:
            return None

        value = self._account.__dict__.get(self._attr, None)

        if value is None:
            return None

        return self._type(value)

    @property
    def name(self) -> str:
        return f"Family Account {self._attr_config.get('name')}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Returns the unit of measurement for this sensor"""
        return self._attr_config.get("native_unit_of_measurement", None)

    @property
    def suggested_display_precision(self) -> int | None:
        """Returns the display precision (2 decimal places)."""
        return self._attr_config.get("suggested_display_precision", None)
