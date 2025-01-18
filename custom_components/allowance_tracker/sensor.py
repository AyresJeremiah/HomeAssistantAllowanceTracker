from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Allowance Tracker sensors."""
    user = config.get("user")
    tracker = hass.data["allowance_tracker"]
    async_add_entities([AllowanceSensor(tracker, user)], True)

class AllowanceSensor(Entity):
    """Representation of an Allowance Tracker sensor."""

    def __init__(self, tracker, user):
        self.tracker = tracker
        self.user = user
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.user.capitalize()} Allowance"

    @property
    def state(self):
        """Return the current balance."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "USD"

    def update(self):
        """Fetch the latest balance from the AllowanceTracker."""
        self._state = self.tracker.get_balance(self.user)