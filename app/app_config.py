import os
import re
import yaml

from dataclasses import dataclass

@dataclass
class AppConfig:
    source: str
    destination: str
    filters: list[str]
    # Regex for exclusions
    excludes: re.Pattern[str] = ''
    key: str = ''

    def __post_init__(self):
        self.key: str = os.getenv('SYNCTHING_API_KEY', '')
        if not self.key:
            raise Exception('No API key found.')

    @classmethod
    def load_from_yaml(cls, config_path: str = '/config/config.yaml') -> AppConfig:
        """ Load configuration and check if minimum requirements are met """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

            if config is None:
                raise Exception('Configuration is empty.')

            return AppConfig(
                source=str(config.get('source', '/files/source/')),
                destination=str(config.get('destination', '/files/destination/')),
                filters=str(config.get('filter', 'ItemFinished')).split(','),
                excludes=re.compile(str(config.get('excludes', '')))
            )
        except FileNotFoundError as e:
            raise Exception(f'Error: The configuration file \'{config_path}\' doesn\'t exists.') from e
        except yaml.YAMLError as yamlError:
            raise Exception(f'Error with parsing the YAML-file: \'{config_path}\'') from yamlError

__all__ = [
    'AppConfig'
]