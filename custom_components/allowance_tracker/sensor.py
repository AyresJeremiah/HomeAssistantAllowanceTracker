from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Allowance Tracker sensors."""
    tracker = hass.data["allowance_tracker"]
    async_add_entities([AllowanceSensor(tracker, user) for user in ["child1", "child2"]], True)

class AllowanceSensor(Entity):
    def __init__(self, tracker, user):
        self.tracker = tracker
        self.user = user
        self._state = None

    @property
    def name(self):
        return f"{self.user.capitalize()} Allowance"

    @property
    def state(self):
        return self._state

    def update(self):
        """Fetch balance from the database."""
        self._state = self.tracker.get_balance(self.user)
