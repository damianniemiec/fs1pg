import socket, logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (SwitchEntity, PLATFORM_SCHEMA, ATTR_CURRENT_POWER_W, ATTR_TODAY_ENERGY_KWH)
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_SCAN_INTERVAL

DOMAIN = "fs1pg"

_LOGGER = logging.getLogger(__name__)

CONF_MAC_ADDR = 'mac'
CONF_IP_ADDR = 'ip'
CONF_DEVICE_NAME = 'device_name'
CONF_BROADCAST = 'broadcast'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC_ADDR): cv.string,
    vol.Required(CONF_IP_ADDR): cv.string,
    vol.Optional(CONF_DEVICE_NAME, default='fs1pg'): cv.string,
#     vol.Optional(CONF_SCAN_INTERVAL, default=60)
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
    vol.Optional(CONF_BROADCAST): cv.boolean,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
	add_devices([FS1PG(config['device_name'], config['ip'], config['mac'], config['broadcast'])])

	return True

class FS1PG(SwitchEntity):
	message_on = '0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	message_off = '0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	message_info = '0101030138000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000'
	_state = False
	_emeterParams = {}

	def __init__(self, deviceName, ip, mac, broadcast = False):
		self.deviceName = deviceName
		self.ip = ip
		self.mac = mac.replace(':', '').replace('-', '')
		self.port = 9957
		self.broadcast = broadcast
		self._emeterParams = {}
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
		message = bytearray.fromhex(self.message_on.replace('xxxxxxxxxxxx', self.mac))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if(self.broadcast):
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.sendto(message, (self.ip, self.port))
		sock.close()
		self.update()

	def turn_off(self, **kwargs):
		message = bytearray.fromhex(self.message_off.replace('xxxxxxxxxxxx', self.mac))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if(self.broadcast):
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.sendto(message, (self.ip, self.port))
		sock.close()
		self.update()

	def update(self):
		try:
			message = bytearray.fromhex(self.message_info.replace('xxxxxxxxxxxx', self.mac))
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			if(self.broadcast):
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.settimeout(5)
			sock.sendto(message, (self.ip, self.port))
			data = sock.recv(2048)
			sock.close()
			self._state = data.hex()[113] in [1, '1']
			powerData = self.read_power(data)
			self._emeterParams[ATTR_CURRENT_POWER_W] = "{:.3f}".format(powerData[0])
			self._emeterParams[ATTR_TODAY_ENERGY_KWH] = "{:.3f}".format(powerData[1])
		except (socket.timeout):
			_LOGGER.warning('Connection timeout')
			pass

	def convert_power_bytes(self, powerBytes):
		return powerBytes[3] << 24 & 0xFF000000\
			| powerBytes[0] & 0xFF\
			| powerBytes[1] << 8 & 0xFF00\
			| powerBytes[2] << 16 & 0xFF0000

	def convert_total_power_bytes(self, powerBytes):
		return powerBytes[0] & 0xFF\
			| (powerBytes[1] & 0xFF) << 8\
			| (powerBytes[2] & 0xFF) << 16\
			| (powerBytes[3] & 0xFF) << 24\
			| (powerBytes[4] & 0xFF) << 32\
			| (powerBytes[5] & 0xFF) << 40\
			| (powerBytes[6] & 0xFF) << 48\
			| (powerBytes[7] & 0xFF) << 56

	def read_power(self, socketData):
		if len(socketData) == 956:
			powerBytes = list(socketData[952:956])
			power = self.convert_power_bytes(powerBytes)/1000
			totalPowerBytes = list(socketData[944:952])
			totalPower = self.convert_total_power_bytes(totalPowerBytes)/3600000/1000
			return [power, totalPower]
		return None