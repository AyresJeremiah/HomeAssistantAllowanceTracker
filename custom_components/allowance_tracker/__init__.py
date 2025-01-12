from homeassistant.core import HomeAssistant
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "allowance_tracker"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Allowance Tracker component."""
    hass.data[DOMAIN] = AllowanceTracker(hass)
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
            CREATE TABLE IF NOT EXISTS allowances (
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_allowance(self, user, amount):
        """Add allowance to a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO allowances (user, balance, last_updated)
            VALUES (?, ?, ?)
            ON CONFLICT(user) DO UPDATE SET
                balance = balance + excluded.balance,
                last_updated = excluded.last_updated
        """, (user, amount, datetime.now().isoformat()))
        conn.commit()
        conn.close()

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

    def get_balance(self, user):
        """Get the balance for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM allowances WHERE user = ?", (user,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
