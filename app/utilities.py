import logging
import os
import re
import yaml

from pathlib import Path

from app_config import AppConfig


def initialize_app_config(config_path: str = '/config/config.yaml'):
    """ Load configuration and check if minimum requirements are met """
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError('Configuration is empty.')

    api_key: str = os.getenv('SYNCTHING_API_KEY', '')
    if not api_key:
        raise Exception('No API key found.')

    host: str = os.getenv('SYNCTHING_HOST', '127.0.0.1')
    port: int = os.getenv('SYNCTHING_PORT', 8384)
    is_https: bool = os.getenv('SYNCTHING_HTTPS', '0').lower() in ('1', 'true', 'yes')
    ssl_cert_file: str = os.getenv('SYNCTHING_CERT_FILE')

    return AppConfig(
        api_key,
        host,
        port,
        is_https=is_https,
        ssl_cert_file=ssl_cert_file,
        source=str(config.get('source', '/files/source/')),
        destination=str(config.get('destination', '/files/destination/')),
        filters=str(config.get('filter', 'ItemFinished')).split(','),
        excludes=re.compile(str(config.get('excludes', '')))
    )

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

def process_source_path(source_path: Path, app_config: AppConfig, logger: logging.Logger):
    if not source_path_is_qualified(source_path, app_config, logger):
        return

    destination_path = Path(app_config.destination) / source_path.relative_to(app_config.source)
    link_source_to_destination(source_path, destination_path, logger)

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
    'initialize_app_config',
    'process_source_path'
]