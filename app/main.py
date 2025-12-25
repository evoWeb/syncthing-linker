#!/usr/bin/env python

import yaml
import time

def load_config(config_path='/config/config.yaml'):
    """Lädt die Konfiguration aus einer YAML-Datei."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        print(f"Fehler: Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
        return None
    except yaml.YAMLError as e:
        print(f"Fehler beim Parsen der YAML-Datei: {e}")
        return None

# Konfiguration laden
config = load_config()
print(config)

while True:
    time.sleep(10)