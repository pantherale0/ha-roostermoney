"""Config flow for Natwest Rooster Money integration."""
from __future__ import annotations

import logging
from typing import Any

from pyroostermoney import RoosterMoney
from pyroostermoney.exceptions import InvalidAuthError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Required("exclude_card_pin", default=True): bool,
        vol.Optional("update_interval", default=60): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    hub = RoosterMoney(data["username"], data["password"])

    try:
        await hub.async_login()
    except InvalidAuthError:
        raise InvalidAuth
    except Exception as err:
        raise CannotConnect(err)

    # Return info that you want to store in the config entry.
    return {"title": "Natwest Rooster Money"}


class OptionsFlow(config_entries.OptionsFlow):
    """Handle a options flow for Natwest Rooster Money."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        _LOGGER.debug(">> options.__init()__")
        self.config_entry = config_entry
        self.options = config_entry.options

    async def async_step_init(self, user_input=None) -> FlowResult:
        """handle options flow."""
        _LOGGER.debug(">> options.async_step_init(%s)", user_input)
        entry = self.config_entry
        rooster = self.hass.data[DOMAIN].get(entry.entry_id, None)
        if not rooster:
            return self.async_abort(reason="not_set_up")

        data_schema = vol.Schema(
            {
                vol.Required("username", default=entry.options["username"]): str,
                vol.Required("password", default=entry.options["password"]): str,
                vol.Optional(
                    "exclude_card_pin", default=entry.options["exclude_card_pin"]
                ): bool,
                vol.Optional(
                    "update_interval", default=entry.options["update_interval"]
                ): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Natwest Rooster Money."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
