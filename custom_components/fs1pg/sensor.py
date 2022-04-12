"""Platform for sensor integration."""
from __future__ import annotations

import socket, logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FRIENDLY_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .model import FS1PGSensorEntityDescription

from .const import (
    DOMAIN,
    CONF_MAC_ADDR,
    CONF_IP_ADDR,
    CONF_DEVICE_NAME,
    MANUFACTURER,
    DEFAULT_NAME,
    ATTR_CURRENT_POWER_W,
    ATTR_TODAY_ENERGY_KWH,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Required(CONF_MAC_ADDR): cv.string,
#         vol.Required(CONF_IP_ADDR): cv.string,
#         vol.Optional(CONF_DEVICE_NAME, default="fs1pg"): cv.string,
#         vol.Optional(CONF_FRIENDLY_NAME): cv.string,
#     }
# )


# def setup_platform(hass, config, add_devices, discovery_info=None):
#     sensors: list[FS1PGCurrentPoweSensor] = []
#     for description in SENSOR_TYPES:
#         sensors.append(
#             FS1PGCurrentPoweSensor(
#                 description, config["device_name"], config["ip"], config["mac"]
#             )
#         )
#     add_devices(sensors)

#     return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    name = entry.data[CONF_DEVICE_NAME]
    ip = entry.data[CONF_IP_ADDR]
    mac = entry.data[CONF_MAC_ADDR]

    # async_add_entities([FS1PGCurrentPoweSensor(name, ip, mac)])
    sensors: list[FS1PGCurrentPoweSensor] = []
    for description in SENSOR_TYPES:
        sensors.append(FS1PGCurrentPoweSensor(description, name, ip, mac))
    async_add_entities(sensors)


class FS1PGCurrentPoweSensor(SensorEntity):
    """Representation of a Sensor."""

    entity_description: FS1PGSensorEntityDescription
    message_info = "0101030138000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000"

    def __init__(
        self,
        description: FS1PGSensorEntityDescription,
        deviceName,
        ip,
        mac,
        broadcast=False,
    ):
        self._attr_name = f"{deviceName} {description.name}"
        self._attr_unique_id = f"{deviceName}-{description.key}"
        self.entity_description = description

        self.deviceName = deviceName
        self.ip = ip
        self.mac = mac.replace(":", "").replace("-", "")
        self.port = 9957
        self.broadcast = broadcast
        self._emeterParams = {}
        self.update()

    def update(self) -> None:
        try:
            message = bytearray.fromhex(
                self.message_info.replace("xxxxxxxxxxxx", self.mac)
            )
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(message, (self.ip, self.port))
            data = sock.recv(2048)
            sock.close()
            self._state = data.hex()[113] in [1, "1"]
            powerData = self.read_power(data)
            self._emeterParams[ATTR_CURRENT_POWER_W] = "{:.3f}".format(powerData[0])
            self._emeterParams[ATTR_TODAY_ENERGY_KWH] = "{:.3f}".format(powerData[1])

        except (socket.timeout):
            _LOGGER.debug("Connection timeout")
            pass

    def convert_power_bytes(self, powerBytes):
        return (
            powerBytes[3] << 24 & 0xFF000000
            | powerBytes[0] & 0xFF
            | powerBytes[1] << 8 & 0xFF00
            | powerBytes[2] << 16 & 0xFF0000
        )

    def convert_total_power_bytes(self, powerBytes):
        return (
            powerBytes[0] & 0xFF
            | (powerBytes[1] & 0xFF) << 8
            | (powerBytes[2] & 0xFF) << 16
            | (powerBytes[3] & 0xFF) << 24
            | (powerBytes[4] & 0xFF) << 32
            | (powerBytes[5] & 0xFF) << 40
            | (powerBytes[6] & 0xFF) << 48
            | (powerBytes[7] & 0xFF) << 56
        )

    def read_power(self, socketData):
        if len(socketData) == 956:
            powerBytes = list(socketData[952:956])
            power = self.convert_power_bytes(powerBytes) / 1000
            totalPowerBytes = list(socketData[944:952])
            totalPower = (
                self.convert_total_power_bytes(totalPowerBytes) / 3600000 / 1000
            )
            return [power, totalPower]
        return None

    @property
    def native_value(self) -> float | None:
        if self.entity_description.key == ATTR_CURRENT_POWER_W:
            return self._emeterParams[ATTR_CURRENT_POWER_W]
        elif self.entity_description.key == ATTR_TODAY_ENERGY_KWH:
            return self._emeterParams[ATTR_TODAY_ENERGY_KWH]
