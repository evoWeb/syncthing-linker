#!/usr/bin/env python

import logging
import sys

from pathlib import Path

from app_config import AppConfig


def prepare_logger() -> logging.Logger:
    """ Prepares the logger for the application. """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # stderr is unbuffered!
    )
    return logging.getLogger(__name__)

def link_missing_file(source_path: Path, config: AppConfig, logger: logging.Logger) -> None:
    """ Recreates the directory structure in 'destination' and hardlinks the file. """
    source = str(source_path)

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
        destination_path.hardlink_to(source)
        logger.info(f'Linked {source} to {destination_file}')
    except FileExistsError:
        return
    except OSError as e:
        logger.error(f'Error linking {source} to {destination_file}: {e}')
        return

def main():
    logger = prepare_logger()
    app_config = AppConfig.load_from_yaml()

    source: str = app_config.source
    logger.info(f'search in {source}')

    source_path = Path(source)
    if not source_path.exists():
        logger.error(f'Ignoring event for {source} because it does not exist.')
        return

    for source_file in source_path.rglob('*'):
        # Skip directories
        if source_file.is_dir():
            continue

        # Check exclusions
        if app_config.excludes.match(str(source_file)):
            logger.info(f'Ignoring {source_file} because it matches the exclusion pattern')
            continue

        link_missing_file(source_file, app_config, logger)

if __name__ == '__main__':
    main()
