#!/usr/bin/env python

import logging
import time

from pathlib import Path

from syncthing.config import Config
from syncthing.database import Database
from syncthing.events import Events
from syncthing.system import System
from syncthing.service_config import ServiceConfig
from syncthing.syncthing_exception import SyncthingException
from app_config import AppConfig
from utilities import link_source_to_destination
from utilities import prepare_logger
from utilities import source_path_is_qualified

def check_service_config(config: ServiceConfig, logger: logging.Logger) -> None:
    """ Checks the connection to the Syncthing API """
    system: System = System(config)

    # supports GET/POST semantics
    sync_errors = system.errors()
    system.clear()

    if sync_errors:
        for e in sync_errors:
            logger.error(e)
        raise RuntimeError('Accessing Syncthing API failed.')

def get_source_path_for_event(event: dict, config: Config, database: Database) -> Path | None:
    data: dict = event.get('data', {})
    if data.get('error') or (not data.get('folder') and not data.get('item')):
        return None

    try:
        folder: dict = config.folder(data.get('folder'))
        file: dict = database.file(data.get('folder'), data.get('item'))
        source_path: Path = Path(folder.get('path')) / file.get('local', {}).get('name')
    except KeyError:
        return None

    return source_path

def process_event(event: dict, app_config: AppConfig, config: Config, database: Database, logger: logging.Logger) -> None:
    source_path = get_source_path_for_event(event, config, database)

    if not source_path_is_qualified(source_path, app_config, logger):
        return

    destination_path = Path(app_config.destination) / source_path.relative_to(app_config.source)
    link_source_to_destination(source_path, destination_path, logger)

def main():
    logger = prepare_logger()
    app_config = AppConfig.load_from_yaml()
    check_service_config(app_config, logger)
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
        except KeyboardInterrupt:
            del event_stream
            print("\r", end='')
            logger.info('Stop waiting for events')
            healthy = False

if __name__ == '__main__':
    main()
