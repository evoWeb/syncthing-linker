#!/usr/bin/env python

from pathlib import Path

from app_config import AppConfig
from utilities import link_source_to_destination
from utilities import prepare_logger
from utilities import source_path_is_qualified

def main():
    logger = prepare_logger()
    app_config = AppConfig.load_from_yaml()

    source: str = app_config.source
    logger.info(f'search in {source}')

    source_path = Path(source)
    if not source_path.exists():
        logger.error(f'Ignoring event for {source} because it does not exist.')
        return

    for source_path in source_path.rglob('*'):
        if not source_path_is_qualified(source_path, app_config, logger):
            continue

        destination_path = Path(app_config.destination) / source_path.relative_to(app_config.source)
        link_source_to_destination(source_path, destination_path, logger)

if __name__ == '__main__':
    main()
