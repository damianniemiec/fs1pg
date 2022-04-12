from __future__ import annotations

from typing import Final

from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from .model import FS1PGSensorEntityDescription
from homeassistant.const import POWER_WATT, ENERGY_KILO_WATT_HOUR

DOMAIN: Final = "fs1pg"
CONF_MAC_ADDR: Final = "mac"
CONF_IP_ADDR: Final = "ip"
CONF_DEVICE_NAME: Final = "device_name"
CONF_BROADCAST: Final = "broadcast"

MANUFACTURER: Final = "Ferguson"
DEFAULT_NAME: Final = "FS1PG"

ATTR_CURRENT_POWER_W: Final = "current_power_w"
ATTR_TODAY_ENERGY_KWH: Final = "today_energy_kwh"

SENSOR_TYPES: Final[tuple[FS1PGSensorEntityDescription, ...]] = (
    FS1PGSensorEntityDescription(
        key=ATTR_CURRENT_POWER_W,
        name="Current Power (W)",
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    FS1PGSensorEntityDescription(
        key=ATTR_TODAY_ENERGY_KWH,
        name="Daily power (KWh)",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)
