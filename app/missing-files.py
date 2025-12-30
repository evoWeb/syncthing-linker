#!/usr/bin/env python

from pathlib import Path

from app_config import AppConfig


def link_missing_file(source_path: Path, config: AppConfig) -> None:
    """ Recreates the directory structure in 'destination' and hardlinks the file. """
    source = str(source_path)

    destination_file: str = config.destination + source[len(config.source):]
    destination_path = Path(destination_file)

    destination_parent = destination_path.parent
    if not destination_parent.exists():
        destination_parent.mkdir(parents=True, exist_ok=True)
        print(f'Created parent directory {destination_parent} for {destination_file}.')

    if destination_path.exists():
        # we don't want to overwrite existing files
        return

    try:
        destination_path.hardlink_to(source)
        print(f'Linked {source} to {destination_file}')
    except FileExistsError:
        return
    except OSError as e:
        print(f'Error linking {source} to {destination_file}: {e}')
        return


def main():
    config = AppConfig.load_from_yaml()

    source: str = config.source
    print(f'search in {source}')

    source_path = Path(source)
    if not source_path.exists():
        print(f'Ignoring event for {source} because it does not exist.')
        return

    for source_file in source_path.rglob('*'):
        # Skip directories
        if source_file.is_dir():
            continue

        # Check exclusions
        if config.excludes.match(str(source_file)):
            print(f'Ignoring {source_file} because it matches the exclusion pattern')
            continue

        link_missing_file(source_file, config)

if __name__ == '__main__':
    main()
