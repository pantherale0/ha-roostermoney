"""Sensors for rooster money."""
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any
import logging
import json

from pyroostermoney import RoosterMoney
from pyroostermoney.child import ChildAccount, Pot
from pyroostermoney.family_account import FamilyAccount

from homeassistant.components.sensor.const import SensorStateClass
from .update_coordinator import RoosterCoordinator
from .helpers import JobEncoder

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

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
    # Get a list of all children in account
    children = hass.data[DOMAIN][config_entry.entry_id].rooster.children
    entities = []
    for child in children:
        entities.append(
            RoosterChildMoneySensor(
                coordinator=hass.data[DOMAIN][config_entry.entry_id],
                idx=None,
                child_id=child.user_id,
            )
        )
        entities.append(
            RoosterChildLastTransactionSensor(
                coordinator=hass.data[DOMAIN][config_entry.entry_id],
                idx=None,
                child_id=child.user_id,
            )
        )
        entities.append(
            RoosterChildJobSensor(
                coordinator=hass.data[DOMAIN][config_entry.entry_id],
                idx=None,
                child_id=child.user_id,
            )
        )
        for pot in child.pots:
            entities.append(
                RoosterPotSensor(
                    coordinator=hass.data[DOMAIN][config_entry.entry_id],
                    idx=None,
                    child_id=child.user_id,
                    pot_id=pot.pot_id,
                )
            )

    # Create the family account entities
    family_account = hass.data[DOMAIN][config_entry.entry_id].rooster.family_account
    for attr in FAMILY_ACCOUNT_ATTR_MAP:
        entities.append(
            RoosterFamilySensor(
                family_account, hass.data[DOMAIN][config_entry.entry_id].rooster, attr
            )
        )
    entities.append(
        RoosterFamilyTransactionSensor(
            family_account, hass.data[DOMAIN][config_entry.entry_id].rooster
        )
    )

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

    def __init__(self, coordinator: RoosterCoordinator, idx, child_id: int) -> None:
        super().__init__(coordinator, idx, child_id, "last_transaction")

    @property
    def name(self) -> str:
        return f"Last Transaction"

    @property
    def native_value(self) -> float:
        """Returns the native value of the entity."""
        return self._child.latest_transaction.amount

    @property
    def native_unit_of_measurement(self) -> str:
        """Returns the unit of measurement for this sensor."""
        return str(self._child.latest_transaction.currency.upper())

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
            "description": self._child.latest_transaction.description,
            "extra_description": self._child.latest_transaction.extended_description,
            "type": self._child.latest_transaction.transaction_type,
            "balance": self._child.latest_transaction.new_balance,
        }


class RoosterPotSensor(RoosterChildEntity, SensorEntity):
    """A Rooster pot."""

    def __init__(
        self,
        coordinator: RoosterCoordinator,
        idx,
        child_id: int,
        pot_id: str,
    ) -> None:
        super().__init__(coordinator, idx, child_id, f"{pot_id}_pot")
        self._attr = CHILD_ACCOUNT_ATTR_MAP.get("pot")
        self._pot_id = pot_id

    @property
    def _pot(self) -> Pot:
        """Gets the pot."""
        return [x for x in self._child.pots if x.pot_id == self._pot_id][0]

    @property
    def name(self) -> str:
        return str(self._attr.get("name")).format(pot_name=self._pot.name)

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

    async def async_boost_pot(
        self, amount: float, description: str = "Boost from Home Assistant"
    ):
        """Boost a pot."""
        await self._pot.add_to_pot(amount, description)


class RoosterChildMoneySensor(RoosterChildEntity, SensorEntity):
    """A sensor for Rooster Money."""

    def __init__(self, coordinator: RoosterCoordinator, idx, child_id: int) -> None:
        super().__init__(coordinator, idx, child_id, "pocket_money")

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

    @property
    def entity_picture(self) -> str | None:
        return self._child.profile_image


class RoosterChildJobSensor(RoosterChildEntity, SensorEntity):
    """A job sensor that contains an array of jobs for the current allowance period."""

    def __init__(self, coordinator: RoosterCoordinator, idx, child_id: int) -> None:
        super().__init__(coordinator, idx, child_id, "allowance_jobs")

    @property
    def name(self) -> str:
        return "Current Week Jobs"

    @property
    def native_value(self) -> int:
        return len(self._child.jobs)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return "Jobs(s)"

    @property
    def state_class(self) -> SensorStateClass | str | None:
        return SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str | None:
        return "mdi:broom"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Returns an array of jobs."""
        return {
            "jobs": json.dumps(self._child.jobs, cls=JobEncoder),
            "count": len(self._child.jobs),
        }


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

        # value = self._account.__dict__.get(self._attr, None)
        value = self._account.__dict__
        value = value.get(self._attr)

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

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return self._attr_config.get("device_class", None)


class RoosterFamilyTransactionSensor(RoosterFamilyEntity, SensorEntity):
    """A sensor for Rooster Money."""

    def __init__(self, account: FamilyAccount, session: RoosterMoney) -> None:
        super().__init__(account, session, "latest_transaction")

    @property
    def native_value(self) -> float:
        if self._account.latest_transaction is None:
            return 0
        return self._account.latest_transaction["amount"]

    @property
    def suggested_display_precision(self) -> int | None:
        """Returns the display precision (2 decimal places)."""
        return 2

    @property
    def name(self) -> str:
        return "Family Account Latest Transaction"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Returns the unit of measurement for this sensor"""
        return "GBP"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.MONETARY

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "month_transactions": self._account.current_month_transactions,
            "type": self._account.latest_transaction["type"],
            "reason": self._account.latest_transaction["reason"],
        }
