"""Constants for the Natwest Rooster Money integration."""

import voluptuous as vol
from homeassistant.components.sensor import SensorDeviceClass

DOMAIN = "rooster_money"
CHILD_ACCOUNT_ATTR_MAP = {
    "pocket_money": {
        "name": "Pocket Money",
        "type": float,
        "native_unit_of_measurement": "GBP",
        "suggested_display_precision": 2,
        "device_class": SensorDeviceClass.MONETARY,
    },
    "pot": {
        "name": "{pot_name} Pot",
        "type": float,
        "native_unit_of_measurement": "GBP",
        "suggested_display_precision": 2,
        "device_class": SensorDeviceClass.MONETARY,
    },
}

FAMILY_ACCOUNT_ATTR_MAP = {
    "sort_code": {"name": "Sort Code", "type": str},
    "account_number": {"name": "Account Number", "type": str},
    "suggested_monthly_transfer": {
        "name": "Suggested Monthly Transfer",
        "type": float,
        "native_unit_of_measurement": "GBP",
        "suggested_display_precision": 2,
        "device_class": SensorDeviceClass.MONETARY,
    },
    "balance": {
        "name": "Balance",
        "type": float,
        "native_unit_of_measurement": "GBP",
        "suggested_display_precision": 2,
        "device_class": SensorDeviceClass.MONETARY,
    },
}

ENTITY_SERVICES = {
    "create_standing_order": {
        "schema": {
            vol.Required("amount"): float,
            vol.Optional("day", default="Monday"): str,
            vol.Required("frequency"): str,
            vol.Required("tag"): str,
            vol.Required("title"): str,
        },
        "function": "async_create_standing_order",
        "required_features": None,
    },
    "delete_standing_order": {
        "schema": {vol.Required("regular_id"): str},
        "function": "async_delete_standing_order",
        "required_features": None,
    },
    "get_standing_orders": {
        "schema": {},
        "function": "async_get_standing_orders",
        "required_features": None,
    },
    "perform_action_on_job": {
        "schema": {vol.Required("job_id"): int, vol.Required("action"): str},
        "function": "async_perform_action_on_job",
        "required_features": None,
    },
    "update_allowance": {
        "schema": {vol.Required("active"): bool, vol.Required("amount"): float},
        "function": "async_update_allowance",
        "required_features": None,
    }
}
