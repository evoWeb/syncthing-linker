import re

from dataclasses import dataclass

from syncthing.service_config import ServiceConfig


@dataclass
class AppConfig(ServiceConfig):
    source: str = '/files/source/'
    destination: str = '/files/destination/'
    filters: list[str] = None
    # Regex for exclusions
    excludes: re.Pattern[str] = ''
