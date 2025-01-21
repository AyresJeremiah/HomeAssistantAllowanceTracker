from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Allowance Tracker sensors."""
    if discovery_info is None:
        return

    kids = discovery_info.get("kids", [])
    tracker = hass.data["allowance_tracker"]

    sensors = []
    for kid in kids:
        sensor = AllowanceSensor(tracker, kid, hass)
        sensors.append(sensor)

    async_add_entities(sensors, True)


class AllowanceSensor(Entity):
    """Representation of an Allowance Tracker sensor."""

    def __init__(self, tracker, user, hass):
        self.tracker = tracker
        self.user = user
        self.hass = hass
        self._state = None

        # Register the sensor in hass.data for real-time updates
        if "allowance_tracker_sensors" not in self.hass.data:
            self.hass.data["allowance_tracker_sensors"] = {}
        self.hass.data["allowance_tracker_sensors"][user] = self

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.user.capitalize()} Allowance"

    @property
    def state(self):
        """Return the current balance."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"allowance_tracker_{self.user}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "USD"

    async def async_update(self):
        """Fetch the latest balance from the AllowanceTracker."""
        self._state = self.tracker.get_balance(self.user)

    def update_balance(self):
        """Update the sensor state when called externally."""
        self._state = self.tracker.get_balance(self.user)
        self.async_write_ha_state()
