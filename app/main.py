#!/usr/bin/env python

import logging
import os
import sys
import yaml

from pathlib import Path

from Syncthing.Syncthing import Syncthing
from Syncthing.Syncthing import syncthing_factory
from Syncthing.SyncthingError import SyncthingError

class Main:
    _logger: logging.Logger
    _key: str
    _config: dict

    def __init__(self):
        self.prepare_logger()

        self.key = self.get_api_key()
        self.config = self.load_config()

        filters: list[str] | None = None
        if self.config.get('filters', '') != '':
            filters = self.config['filters'].split(',')

        syncthing = syncthing_factory()
        self.check_connection(syncthing)

        self.loop_events(syncthing, filters)

    def prepare_logger(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=sys.stderr  # stderr is unbuffered!
        )
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def get_api_key() -> str:
        key: str = os.getenv('SYNCTHING_API_KEY', '')
        if key == '':
            raise Exception('No API key found.')
        return key

    @staticmethod
    def load_config(config_path: str = '/config/config.yaml') -> dict | None:
        """ Load configuration and check if minimum requirements are met """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)

            if config_data is None:
                raise Exception('Configuration is empty.')

            if 'source' not in config_data:
                config_data['source'] = '/files/source/'
            if 'destination' not in config_data:
                config_data['destination'] = '/files/destination/'
            if 'filters' not in config_data:
                config_data['filters'] = 'ItemFinished'

            return config_data
        except FileNotFoundError:
            print(f"Fehler: Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
            return None
        except yaml.YAMLError as yamlError:
            print(f"Fehler beim Parsen der YAML-Datei: {yamlError}")
            return None

    @staticmethod
    def check_connection(wrapper: Syncthing) -> None:
        """ Checks the connection to the Syncthing API """
        wrapper.system.connections()

        # supports GET/POST semantics
        sync_errors = wrapper.system.errors()
        wrapper.system.clear()

        if sync_errors:
            for e in sync_errors:
                print(e)
                exit(1)

    def loop_events(self, syncthing: Syncthing, filters: list[str]) -> None:
        self._logger.info('Waiting for events')
        last_seen_id: int | None = None
        while True:
            if last_seen_id:
                event_stream = syncthing.events(limit=10, filters=filters, last_seen_id=last_seen_id)
            else:
                event_stream = syncthing.events(limit=10, filters=filters)

            try:
                for event in event_stream:
                    self.process_event(syncthing, event)
            except SyncthingError:
                last_seen_id = event_stream.last_seen_id
            except KeyboardInterrupt:
                event_stream.stop()
                print('bye bye')
                exit(0)

    def process_event(self, syncthing: Syncthing, event: dict) -> None:
        data: dict = event.get('data', {})
        if data.get('error', None) is not None or 'folder' not in data or 'item' not in data:
            return

        try:
            folder: dict = syncthing.config.folder(data['folder'])
            file: dict = syncthing.database.file(data['folder'], data['item'])
            source = folder['path'] + file['local']['name']
        except KeyError:
            return

        source_path = Path(source)
        if not source_path.exists():
            self._logger.info(f'Ignoring event for {source} because it does not exist.')
            return
        if not source.startswith(self.config['source']):
            self._logger.info(f'Ignoring event for {source} because it does not start with {self.config["source"]}.')
            return

        destination: str = self.config['destination'] + source[len(self.config['source']):]
        destination_path = Path(destination)

        destination_parent = Path(destination_path.parent)
        if not destination_parent.exists():
            destination_parent.mkdir(parents=True, exist_ok=True)
            self._logger.info(f'Created parent directory {destination_parent} for {destination}.')

        if destination_path.exists():
            # we don't want to overwrite existing files
            return

        try:
            destination_path.hardlink_to(source)
            self._logger.info(f'Linked {source} to {destination}')
        except FileExistsError:
            return
        except OSError as e:
            self._logger.error(f'Error linking {source} to {destination}: {e}')
            return

if __name__ == '__main__':
    Main()