#!/usr/bin/env python

import logging
import sys

from pathlib import Path

from Syncthing.Syncthing import Syncthing
from Syncthing.Syncthing import syncthing_factory
from Syncthing.SyncthingException import SyncthingException
from AppConfig import AppConfig

class Main:
    logger: logging.Logger
    config: AppConfig

    def __init__(self):
        self.logger = self.prepare_logger()
        self.config = AppConfig.load_from_yaml()

        syncthing = syncthing_factory(self.config.key)
        self.check_connection(syncthing)
        self.loop_events(syncthing)

    @staticmethod
    def prepare_logger() -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=sys.stderr  # stderr is unbuffered!
        )
        return logging.getLogger(__name__)

    @staticmethod
    def check_connection(syncthing: Syncthing) -> None:
        """ Checks the connection to the Syncthing API """
        syncthing.system.connections()

        # supports GET/POST semantics
        sync_errors = syncthing.system.errors()
        syncthing.system.clear()

        if sync_errors:
            for e in sync_errors:
                print(e)
            exit(1)

    def loop_events(self, syncthing: Syncthing) -> None:
        self.logger.info('Waiting for events')
        last_seen_id: int | None = None
        while True:
            if last_seen_id:
                event_stream = syncthing.events(filters=self.config.filters, last_seen_id=last_seen_id)
            else:
                event_stream = syncthing.events(filters=self.config.filters)

            try:
                for event in event_stream:
                    self.process_event(syncthing, event)
                    last_seen_id = event['id']
            except SyncthingException:
                continue
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
            source_file = folder['path'].rstrip('/') + '/' + file['local']['name']
        except KeyError:
            return

        source_path = Path(source_file)
        if not source_path.exists():
            self.logger.info(f'Ignoring event for {source_file} because it does not exist.')
            return
        if source_path.is_dir():
            self.logger.info(f'Ignoring event for {source_file} because it\'s a folder.')
            return
        if not source_file.startswith(self.config.source):
            self.logger.info(f'Ignoring event for {source_file} because it does not start with {self.config.source}.')
            return
        if self.config.excludes.match(str(source_file)):
            print(f'Ignoring {source_file} because it matches the exclusion pattern')
            return

        destination_file: str = self.config.destination + source_file[len(self.config.source):]
        destination_path = Path(destination_file)

        destination_parent = destination_path.parent
        if not destination_parent.exists():
            destination_parent.mkdir(parents=True, exist_ok=True)
            self.logger.info(f'Created parent directory {destination_parent} for {destination_file}.')

        if destination_path.exists():
            # we don't want to overwrite existing files
            return

        try:
            destination_path.hardlink_to(source_file)
            self.logger.info(f'Linked {source_file} to {destination_file}')
        except FileExistsError:
            return
        except OSError as e:
            self.logger.error(f'Error linking {source_file} to {destination_file}: {e}')
            return

if __name__ == '__main__':
    Main()

__all__ = [
    'Main'
]