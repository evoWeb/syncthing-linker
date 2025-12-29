import os
import yaml

from dataclasses import dataclass

@dataclass
class AppConfig:
    source: str
    destination: str
    filters: list[str]
    excludes: str = ''
    key: str = ''

    def __post_init__(self):
        self.key: str = os.getenv('SYNCTHING_API_KEY', '')
        if self.key == '':
            raise Exception('No API key found.')

    @classmethod
    def load_from_yaml(cls, config_path: str = '/config/config.yaml') -> AppConfig:
        """ Load configuration and check if minimum requirements are met """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

            if config is None:
                raise Exception('Configuration is empty.')

            if 'source' not in config:
                config['source'] = '/files/source/'
            if 'destination' not in config:
                config['destination'] = '/files/destination/'
            if 'filters' not in config:
                config['filters'] = 'ItemFinished'

            if isinstance(config['filters'], str):
                config['filters'] = config['filters'].split(',')

            return AppConfig(
                source=config.get('source'),
                destination=config.get('destination'),
                filters=config.get('filters', []),
                excludes=config.get('excludes', '')
            )
        except FileNotFoundError:
            raise Exception(f'Fehler: Die Konfigurationsdatei "{config_path}" wurde nicht gefunden.')
        except yaml.YAMLError as yamlError:
            raise Exception(f'Fehler beim Parsen der YAML-Datei: {yamlError}')
