import os
import re
import yaml

from dataclasses import dataclass

from syncthing.service_config import ServiceConfig


@dataclass
class AppConfig(ServiceConfig):
    source: str = '/files/source/'
    destination: str = '/files/destination/'
    filters: list[str] = None
    # Regex for exclusions
    excludes: re.Pattern[str] = ''
    key: str = ''

    def __post_init__(self):
        self.api_key = os.getenv('SYNCTHING_API_KEY', '')
        if not self.api_key:
            raise Exception('No API key found.')

        self.host = os.getenv('SYNCTHING_HOST', '127.0.0.1')
        self.post = os.getenv('SYNCTHING_PORT', 8384)
        self.is_https = os.getenv('SYNCTHING_HTTPS', '0').lower() in ('1', 'true', 'yes')
        self.ssl_cert_file = os.getenv('SYNCTHING_CERT_FILE')

    @classmethod
    def load_from_yaml(cls, config_path: str = '/config/config.yaml') -> AppConfig:
        """ Load configuration and check if minimum requirements are met """
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        if config is None:
            raise ValueError('Configuration is empty.')

        return AppConfig(
            source=str(config.get('source', '/files/source/')),
            destination=str(config.get('destination', '/files/destination/')),
            filters=str(config.get('filter', 'ItemFinished')).split(','),
            excludes=re.compile(str(config.get('excludes', '')))
        )

__all__ = [
    'AppConfig'
]