#!/usr/bin/env python

import os
import yaml

from Syncthing.Syncthing import Syncthing
from Syncthing.Syncthing import syncthing_factory
from Syncthing.SyncthingError import SyncthingError

class Main:
    def __init__(self):
        self.key = self.get_api_key()
        self.config = self.load_config()

        filters: list[str] | None = None
        if self.config.get('filters', '') != '':
            filters = self.config['filters'].split(',')

        syncthing = syncthing_factory()
        self.check_connection(syncthing)

        self.loop_events(syncthing, filters)

    @staticmethod
    def get_api_key() -> str:
        key: str = os.getenv('SYNCTHING_API_KEY', '')
        if key == '':
            raise Exception('No API key found.')
        return key

    @staticmethod
    def load_config(config_path ='/config/config.yaml') -> dict | None:
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

    def loop_events(self, syncthing: Syncthing, filters) -> None:
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

    def process_event(self, syncthing: Syncthing, event) -> None:
        if event['data']['error'] is str:
            return
        file = syncthing.database.file(event['data']['folder'], event['data']['item'])
        print(syncthing.statistics.folder())
        print(event)
        print(file)

if __name__ == '__main__':
    Main()