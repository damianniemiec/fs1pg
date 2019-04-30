import socket, logging
from homeassistant.components.switch import (SwitchDevice,\
PLATFORM_SCHEMA, ATTR_CURRENT_POWER_W, ATTR_TODAY_ENERGY_KWH)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
	add_devices([FS1PG(config['device_name'], config['ip'], config['mac'])])

class FS1PG(SwitchDevice):
	message_on = '0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	message_off = '0101010180000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	message_info = '0101030138000000010000005c6c5c6c0000000000000000000000000000000000000000000000000000000000000000xxxxxxxxxxxx0000'
	_state = False
	_emeterParams = {}

	def __init__(self, deviceName, ip, mac):
		self.deviceName = deviceName
		self.ip = ip
		self.mac = mac.replace(':', '').replace('-', '')
		self.port = 9957
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
		sock.sendto(message, (self.ip, self.port))
		sock.close()
		self.update()

	def turn_off(self, **kwargs):
		message = bytearray.fromhex(self.message_off.replace('xxxxxxxxxxxx', self.mac))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(message, (self.ip, self.port))
		sock.close()
		self.update()

	def update(self):
		try:
			message = bytearray.fromhex(self.message_info.replace('xxxxxxxxxxxx', self.mac))
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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