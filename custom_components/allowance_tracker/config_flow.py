from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class AllowanceTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Allowance Tracker."""

    VERSION = 1
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return AllowanceTrackerOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Config Flow: async_step_user called")

        if user_input is not None:
            _LOGGER.debug("Config Flow: User input received: %s", user_input)
            return self.async_create_entry(title="Allowance Tracker", data=user_input)

        _LOGGER.debug("Config Flow: Showing user form")
        return self.async_show_form(step_id="user")
    

class AllowanceTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Allowance Tracker."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        _LOGGER.debug("Options Flow: Initialized for config entry: %s", config_entry)

    async def async_step_init(self, user_input=None):
        """Manage options."""
        _LOGGER.debug("Options Flow: async_step_init called")

        if user_input is not None:
            # Get existing kids
            existing_kids = self.config_entry.options.get("kids", [])
            _LOGGER.debug("Existing kids before update: %s", existing_kids)

            # Add new kids to the array
            new_kids = [kid.strip() for kid in user_input["kids"].split("\n") if kid.strip()]
            updated_kids = list(set(existing_kids + new_kids))  # Merge and remove duplicates
            _LOGGER.debug("Updated kids list: %s", updated_kids)

            # Save the updated array
            return self.async_create_entry(title="", data={"kids": updated_kids})

        # Current options
        current_kids = self.config_entry.options.get("kids", [])
        _LOGGER.debug("Options Flow: Current kids list: %s", current_kids)

        # Form schema for editing kids
        schema = vol.Schema(
            {
                vol.Optional(
                    "kids",
                    default="",
                ): str,
            }
        )
        _LOGGER.debug("Options Flow: Showing options form for adding new kids")
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={},
        )
