from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription


@dataclass
class FS1PGSensorEntityDescription(SensorEntityDescription):
    """Class describing FS1PG sensor entities."""
