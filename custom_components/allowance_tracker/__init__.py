from homeassistant.core import HomeAssistant
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Allowance Tracker component."""
    if DOMAIN not in config:
        return True

    hass.data[DOMAIN] = AllowanceTracker(hass)
    hass.data["allowance_tracker_sensors"] = {}  # Store references to sensors
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    # Register services
    async def add_allowance(call):
        user = call.data.get("user")
        amount = call.data.get("amount")
        hass.data[DOMAIN].add_allowance(user, amount)

    async def deduct_allowance(call):
        user = call.data.get("user")
        amount = call.data.get("amount")
        hass.data[DOMAIN].deduct_allowance(user, amount)

    hass.services.async_register(DOMAIN, "add_allowance", add_allowance)
    hass.services.async_register(DOMAIN, "deduct_allowance", deduct_allowance)

    return True



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Allowance Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, AllowanceTracker(hass))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    tracker = AllowanceTracker(hass)
    hass.data[DOMAIN] = tracker

    # Load kids from entry options
    kids = entry.options.get("kids", [])
    tracker.set_kids(kids)
    
    return True


import sqlite3
from datetime import datetime

class AllowanceTracker:
    def __init__(self, hass):
        self.hass = hass
        self.db_path = hass.config.path("allowance_tracker.db")
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL UNIQUE,
                balance REAL NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def set_kids(self, kids):
        """Update the list of kids and initialize their balances if necessary."""
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE allowances
            SET balance = balance + ?, last_updated = ?
            WHERE user = ?
        """, (amount, datetime.now().isoformat(), user))
        conn.commit()
        conn.close()
        # Trigger sensor update
        self.update_sensor(user)

    def deduct_allowance(self, user, amount):
        """Deduct allowance from a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE allowances
            SET balance = balance - ?, last_updated = ?
            WHERE user = ?
        """, (amount, datetime.now().isoformat(), user))
        conn.commit()
        conn.close()
        # Trigger sensor update
        self.update_sensor(user)

    def get_balance(self, user):
        """Get the balance for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM allowances WHERE user = ?", (user,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0

    def update_sensor(self, user):
        """Trigger an update for the corresponding sensor."""
        sensor = self.hass.data["allowance_tracker_sensors"].get(user)
        if sensor:
            sensor.update_balance()
