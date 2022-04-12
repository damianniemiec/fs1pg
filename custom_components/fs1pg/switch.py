from __future__ import annotations

import socket, logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (
    SwitchEntity,
    PLATFORM_SCHEMA,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FRIENDLY_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntityDescription

from .const import DOMAIN, CONF_MAC_ADDR, CONF_IP_ADDR, CONF_DEVICE_NAME

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
#     add_devices([FS1PG(config["device_name"], config["ip"], config["mac"])])

#     return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    name = entry.data[CONF_DEVICE_NAME]
    mac = entry.data[CONF_MAC_ADDR]
    ip = entry.data[CONF_IP_ADDR]

    async_add_entities([FS1PG(deviceName=name, ip=ip, mac=mac)])


class FS1PG(SwitchEntity):
    entity_description: SwitchEntityDescription
    message_on = "0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    message_off = "0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    message_info = "0101030138000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000"
    _state = False
    _emeterParams = {}

    def __init__(self, deviceName, ip, mac, broadcast=False):
        self.deviceName = deviceName
        self.ip = ip
        self.mac = mac.replace(":", "").replace("-", "")
        self.port = 9957
        self.broadcast = broadcast

        self._attr_name = f"{deviceName} switch"
        self._attr_unique_id = f"{self.mac}"

        self.update()

    @property
    def name(self):
        return self.deviceName

    @property
    def is_on(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._emeterParams

    def turn_on(self, **kwargs):
        message = bytearray.fromhex(self.message_on.replace("xxxxxxxxxxxx", self.mac))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.broadcast:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message, (self.ip, self.port))
        sock.close()
        self.update()

    def turn_off(self, **kwargs):
        message = bytearray.fromhex(self.message_off.replace("xxxxxxxxxxxx", self.mac))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.broadcast:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message, (self.ip, self.port))
        sock.close()
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

        except (socket.timeout):
            _LOGGER.debug("Connection timeout")
            pass
