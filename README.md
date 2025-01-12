# Allowance Tracker

A Home Assistant custom component to track and manage allowances for users, storing balances in an SQLite database. With this component, you can easily automate periodic allowance updates, view user balances, and manage transactions through Home Assistant services.

---

## Features

- **Track Allowances**: Maintain balances for multiple users.
- **Automate Allowances**: Add allowances on a schedule using Home Assistant automations.
- **Custom Services**: Add or deduct funds using Home Assistant's service calls.
- **SQLite Storage**: Persistent storage for balances and transaction history.
- **Sensors**: (Optional) Display user balances as sensors in Home Assistant.

---

## Installation

### **Via HACS**
1. Go to HACS in your Home Assistant instance.
2. Add this repository as a custom repository:
   - URL: `https://github.com/AyresJeremiah/HomeAssistantAllowanceTracker`
   - Category: `Integration`
3. Find and install the **Allowance Tracker** integration in HACS.
4. Restart Home Assistant.

### **Manual Installation**
1. Clone or download this repository:
   ```bash
   git clone https://github.com/AyresJeremiah/HomeAssistantAllowanceTracker.git
   ```
2. Copy the `allowance_tracker` folder to your Home Assistant custom components directory:
   ```bash
   cp -R HomeAssistantAllowanceTracker/custom_components/allowance_tracker /config/custom_components/
   ```
3. Restart Home Assistant.

---

## Configuration

Add the following to your `configuration.yaml` file:

```yaml
allowance_tracker:
```

Restart Home Assistant to load the configuration.

---

## Usage

### **Available Services**
The Allowance Tracker provides the following services:

#### **1. Add Allowance**
- Service: `allowance_tracker.add_allowance`
- Parameters:
  - `user` (string): The name of the user to update.
  - `amount` (float): The amount to add to the user's balance.

Example:
```yaml
service: allowance_tracker.add_allowance
data:
  user: "child1"
  amount: 10.0
```

#### **2. Deduct Allowance**
- Service: `allowance_tracker.deduct_allowance`
- Parameters:
  - `user` (string): The name of the user to update.
  - `amount` (float): The amount to deduct from the user's balance.

Example:
```yaml
service: allowance_tracker.deduct_allowance
data:
  user: "child1"
  amount: 5.0
```

---

## Sensors (Optional)

You can add sensors to display user balances by enabling them in `sensor.py`. For example, a sensor for "child1" might look like this:

```yaml
sensor:
  - platform: allowance_tracker
    user: "child1"
```

---

## Automation Example

### Add Weekly Allowance
To automate a weekly allowance, add the following to your `automations.yaml`:

```yaml
- alias: "Add Weekly Allowance for Child1"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: allowance_tracker.add_allowance
      data:
        user: "child1"
        amount: 10.0
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Contributions

Contributions are welcome! Feel free to fork the repository and submit a pull request.
