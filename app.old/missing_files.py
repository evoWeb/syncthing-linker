#!/usr/bin/env python

import logging

from pathlib import Path

import utilities

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    app_config = utilities.initialize_app_config()

    source: str = app_config.source
    logger.info(f'search in {source}')

    source_path = Path(source)
    if not source_path.exists():
        logger.error(f'Ignoring event for {source} because it does not exist.')
        return

    for source_path in source_path.rglob('*'):
        utilities.process_source_path(source_path, app_config, logger)

if __name__ == '__main__':
    main()
