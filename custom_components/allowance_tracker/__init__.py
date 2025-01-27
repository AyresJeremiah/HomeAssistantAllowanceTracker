from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .sensor import AllowanceSensor
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

print("DEBUG: Allowance Tracker __init__.py executed")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Allowance Tracker component from configuration.yaml."""
    _LOGGER.debug("Setting up Allowance Tracker from configuration.yaml")
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = AllowanceTracker(hass)
    hass.data["allowance_tracker_sensors"] = {}  # Store references to sensors
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    # Register services
    async def add_allowance(call):
        user = call.data.get("user")
        amount = call.data.get("amount")
        _LOGGER.debug("Adding allowance: user=%s, amount=%s", user, amount)
        hass.data[DOMAIN].add_allowance(user, amount)

    async def deduct_allowance(call):
        user = call.data.get("user")
        amount = call.data.get("amount")
        _LOGGER.debug("Deducting allowance: user=%s, amount=%s", user, amount)
        hass.data[DOMAIN].deduct_allowance(user, amount)

    hass.services.async_register(DOMAIN, "add_allowance", add_allowance)
    hass.services.async_register(DOMAIN, "deduct_allowance", deduct_allowance)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Allowance Tracker from a config entry."""
    _LOGGER.debug("Setting up Allowance Tracker from config entry")

    # Initialize AllowanceTracker
    tracker = AllowanceTracker(hass)
    hass.data[DOMAIN] = tracker

    # Load kids from the database or config entry
    kids = entry.options.get("kids", [])
    if not kids:
        kids = tracker.get_all_kids()  # Retrieve kids from the database
    _LOGGER.debug("Loaded kids: %s", kids)

    # Set kids in the tracker
    tracker.set_kids(kids)

    # Prepare discovery info for the sensor platform
    discovery_info = {"kids": kids}
    hass.data["allowance_tracker_sensors"] = {}

    # Reload the sensor platform
    hass.helpers.discovery.load_platform("sensor", DOMAIN, discovery_info, entry.options)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options updates."""
    _LOGGER.debug("Options updated for Allowance Tracker")

    tracker = hass.data[DOMAIN]
    updated_kids = entry.options.get("kids", [])
    _LOGGER.debug("Updated kids list: %s", updated_kids)

    # Reload the sensor platform with updated kids
    hass.data["allowance_tracker_sensors"] = {}  # Clear existing sensors
    hass.helpers.discovery.load_platform(
        "sensor", DOMAIN, {"kids": updated_kids}, entry.options
    )


    # Handle removed kids
    existing_kids = list(hass.data["allowance_tracker_sensors"].keys())
    for kid in existing_kids:
        if kid not in updated_kids:
            _LOGGER.debug("Removing sensor for kid: %s", kid)
            sensor = hass.data["allowance_tracker_sensors"].pop(kid)
            await sensor.async_remove()




async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Allowance Tracker entry")
    tracker = hass.data[DOMAIN]
    tracker.unload()

    # Clean up integration data
    hass.data.pop(DOMAIN, None)

    return True


import sqlite3
from datetime import datetime

class AllowanceTracker:
    """Main class for managing allowances."""

    def __init__(self, hass):
        self.hass = hass
        self.db_path = hass.config.path("allowance_tracker.db")
        self.kids = []
        self._init_db()
        _LOGGER.debug("AllowanceTracker initialized with database: %s", self.db_path)

    def _init_db(self):
        """Initialize the SQLite database."""
        _LOGGER.debug("Initializing database")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allowances (
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL UNIQUE,
                balance REAL NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def set_kids(self, kids):
        """Update the list of kids and initialize their balances if necessary."""
        _LOGGER.debug("Setting kids: %s", kids)
        self.kids = kids
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for kid in kids:
            cursor.execute("""
                INSERT INTO allowances (user, balance, last_updated)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(user) DO NOTHING
            """, (kid, 0))
        conn.commit()
        conn.close()

    def add_allowance(self, user, amount):
        """Add allowance to a user."""
        _LOGGER.debug("Adding allowance to user=%s, amount=%s", user, amount)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE allowances
            SET balance = balance + ?, last_updated = ?
            WHERE user = ?
        """, (amount, datetime.now().isoformat(), user))
        conn.commit()
        conn.close()
        self.update_sensor(user)

    def deduct_allowance(self, user, amount):
        """Deduct allowance from a user."""
        _LOGGER.debug("Deducting allowance from user=%s, amount=%s", user, amount)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE allowances
            SET balance = balance - ?, last_updated = ?
            WHERE user = ?
        """, (amount, datetime.now().isoformat(), user))
        conn.commit()
        conn.close()
        self.update_sensor(user)

    def get_balance(self, user):
        """Get the balance for a user."""
        _LOGGER.debug("Getting balance for user=%s", user)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM allowances WHERE user = ?", (user,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0

    def update_sensor(self, user):
        """Trigger an update for the corresponding sensor."""
        _LOGGER.debug("Updating sensor for user=%s", user)
        sensor = self.hass.data["allowance_tracker_sensors"].get(user)
        if sensor:
            sensor.update_balance()

    def unload(self):
        """Unload the tracker and clean up resources."""
        _LOGGER.debug("Unloading AllowanceTracker")
