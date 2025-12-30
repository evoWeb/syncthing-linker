import logging
import sys

from pathlib import Path

from app_config import AppConfig


def link_source_to_destination(source_path: Path, destination_path: Path, logger: logging.Logger) -> None:
    """ Hardlinks the source file to the destination. """
    destination_parent = destination_path.parent
    if not destination_parent.exists():
        destination_parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'Created parent directory {destination_parent} for {destination_path}.')

    if destination_path.exists():
        # we don't want to overwrite existing files
        return

    try:
        destination_path.hardlink_to(source_path)
        logger.info(f'Linked {source_path} to {destination_path}')
    except FileExistsError:
        return
    except OSError as e:
        logger.error(f'Error linking {source_path} to {destination_path}: {e}')
        return

def prepare_logger() -> logging.Logger:
    """ Prepares the logger for the application. """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # stderr is unbuffered!
    )
    return logging.getLogger(__name__)

def source_path_is_qualified(source_path: Path, app_config: AppConfig, logger: logging.Logger) -> bool:
    """ Checks whether the given path is qualified for linking. """
    if not source_path or not source_path.exists():
        logger.info(f'Ignoring event for {source_path} because it does not exist.')
        return False
    if source_path.is_dir():
        logger.info(f'Ignoring event for {source_path} because it\'s a folder.')
        return False
    if not source_path.is_relative_to(app_config.source):
        logger.info(f'Ignoring event for {source_path} because it does not start with {app_config.source}.')
        return False
    if app_config.excludes.match(str(source_path)):
        logger.info(f'Ignoring {source_path} because it matches the exclusion pattern')
        return False
    return True

__all__ = [
    'link_source_to_destination',
    'prepare_logger',
    'source_path_is_qualified'
]