#!/usr/bin/env python

import os
import time
import yaml
from Syncthing.Syncthing import syncthing_factory

def load_config(config_path = '/config/config.yaml'):
    """Lädt die Konfiguration aus einer YAML-Datei."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        print(f"Fehler: Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
        return None
    except yaml.YAMLError as yamlError:
        print(f"Fehler beim Parsen der YAML-Datei: {yamlError}")
        return None

# Konfiguration laden
config = load_config()
print(config)

key = os.getenv('SYNCTHING_API_KEY', '')
print(key)
if key == '':
    raise Exception('No API key found.')

s = syncthing_factory()

# name spaced by API endpoints
s.system.connections()

# supports GET/POST semantics
sync_errors = s.system.errors()
s.system.clear()

if sync_errors:
    for e in sync_errors:
        print(e)

while True:
    # supports long-polling event
    event_stream = s.events(limit=10)
    for event in event_stream:
        print(event)
        # do something with `event`
        if event_stream.count > 100:
            event_stream.stop()
    time.sleep(10)