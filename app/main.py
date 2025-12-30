#!/usr/bin/env python

import logging
import sys

from pathlib import Path

from syncthing.syncthing import Syncthing
from syncthing.syncthing_exception import SyncthingException
from app_config import AppConfig


def prepare_logger() -> logging.Logger:
    """ Prepares the logger for the application. """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # stderr is unbuffered!
    )
    return logging.getLogger(__name__)

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

def loop_events(syncthing: Syncthing, config: AppConfig, logger: logging.Logger) -> None:
    logger.info('Waiting for events')
    last_seen_id: int | None = None
    while True:
        if last_seen_id:
            event_stream = syncthing.events(filters=config.filters, last_seen_id=last_seen_id)
        else:
            event_stream = syncthing.events(filters=config.filters)

        try:
            for event in event_stream:
                process_event(syncthing, event, config, logger)
                last_seen_id = event.get('id')
        except SyncthingException:
            continue
        except KeyboardInterrupt:
            del event_stream
            print("\r", end='')
            logger.info('Stop waiting for events')
            exit(0)

def process_event(syncthing: Syncthing, event: dict, config: AppConfig, logger: logging.Logger) -> None:
    data: dict = event.get('data', {})
    if data.get('error') or (not data.get('folder') and not data.get('item')):
        return

    try:
        folder: dict = syncthing.config.folder(data.get('folder'))
        file: dict = syncthing.database.file(data.get('folder'), data.get('item'))
        source_path: Path = Path(folder.get('path')) / file.get('local').get('name')
        source_file: str = str(source_path)
    except KeyError:
        return

    if not source_path.exists():
        logger.info(f'Ignoring event for {source_file} because it does not exist.')
        return
    if source_path.is_dir():
        logger.info(f'Ignoring event for {source_file} because it\'s a folder.')
        return
    if not source_file.startswith(config.source):
        logger.info(f'Ignoring event for {source_file} because it does not start with {config.source}.')
        return
    if config.excludes.match(str(source_file)):
        print(f'Ignoring {source_file} because it matches the exclusion pattern')
        return

    destination_path = Path(config.destination) / source_path.relative_to(config.source)
    destination_file: str = str(destination_path)

    destination_parent = destination_path.parent
    if not destination_parent.exists():
        destination_parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'Created parent directory {destination_parent} for {destination_file}.')

    if destination_path.exists():
        # we don't want to overwrite existing files
        return

    try:
        destination_path.hardlink_to(source_file)
        logger.info(f'Linked {source_file} to {destination_file}')
    except FileExistsError:
        return
    except OSError as e:
        logger.error(f'Error linking {source_file} to {destination_file}: {e}')
        return

def main():
    logger = prepare_logger()
    config = AppConfig.load_from_yaml()
    syncthing = Syncthing.create_instance(config.key)

    check_connection(syncthing)
    loop_events(syncthing, config, logger)

if __name__ == '__main__':
    main()
