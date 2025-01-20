from homeassistant import config_entries
from .const import DOMAIN

class AllowanceTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Allowance Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # User submitted the form, proceed with setup
            return self.async_create_entry(title="Allowance Tracker", data=user_input)

        # Show the form
        return self.async_show_form(step_id="user")