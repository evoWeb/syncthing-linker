#!/usr/bin/env python

import logging
import sys
import time

from pathlib import Path

from syncthing.config import Config
from syncthing.database import Database
from syncthing.events import Events
from syncthing.system import System
from syncthing.service_config import ServiceConfig
from syncthing.syncthing_exception import SyncthingException
from app_config import AppConfig

def check_service_config(config: ServiceConfig) -> None:
    """ Checks the connection to the Syncthing API """
    system: System = System(config)

    # supports GET/POST semantics
    sync_errors = system.errors()
    system.clear()

    if sync_errors:
        for e in sync_errors:
            print(e)
        exit(1)

def prepare_logger() -> logging.Logger:
    """ Prepares the logger for the application. """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # stderr is unbuffered!
    )
    return logging.getLogger(__name__)

def process_event(event: dict, app_config: AppConfig, config: Config, database: Database, logger: logging.Logger) -> None:
    data: dict = event.get('data', {})
    if data.get('error') or (not data.get('folder') and not data.get('item')):
        return

    try:
        folder: dict = config.folder(data.get('folder'))
        file: dict = database.file(data.get('folder'), data.get('item'))
        source_path: Path = Path(folder.get('path')) / file.get('local', {}).get('name')
        source_file: str = str(source_path)
    except KeyError:
        return

    if not source_path.exists():
        logger.info(f'Ignoring event for {source_file} because it does not exist.')
        return
    if source_path.is_dir():
        logger.info(f'Ignoring event for {source_file} because it\'s a folder.')
        return
    if not source_file.startswith(app_config.source):
        logger.info(f'Ignoring event for {source_file} because it does not start with {app_config.source}.')
        return
    if app_config.excludes.match(str(source_file)):
        print(f'Ignoring {source_file} because it matches the exclusion pattern')
        return

    destination_path = Path(app_config.destination) / source_path.relative_to(app_config.source)
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
    app_config = AppConfig.load_from_yaml()
    config = Config(app_config)
    database = Database(app_config)
    last_seen_id: int= 0
    healthy = True

    logger.info('Waiting for events')
    while healthy:
        event_stream = Events(app_config, filters=app_config.filters, last_seen_id=last_seen_id)

        try:
            for event in event_stream:
                process_event(event, app_config, config, database, logger)
                last_seen_id = event.get('id')
        except SyncthingException:
            time.sleep(5)
            continue
        except KeyboardInterrupt:
            del event_stream
            print("\r", end='')
            logger.info('Stop waiting for events')
            healthy = False

if __name__ == '__main__':
    main()
