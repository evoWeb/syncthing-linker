# SyncThing Linker

This tool links files from a source folder to a destination folder when a file was uploaded via Syncthing and the
`ItemFinished` event was fired.

The reason why you want this is that once the Hardlink is created, you can remove the file from the sync source without
losing the file on the sync target. This is ideal for devices with limited storage (like mobile phones). You sync to the
target, the linker creates a hardlink, and then you can safely delete the file from your phone.

### Flow comparison
| without Syncthing Linker      | with Syncthing Linker                |
|:------------------------------|:-------------------------------------|
| 1. Create file on mobile      | 1. Create file on mobile             |
| 2. Synchronize to target      | 2a. Synchronize to target            |
|                               | 2b. **Hardlink file to destination** |
| 3. Remove file from mobile    | 3. Remove file from mobile           |
| 4. **File is lost on target** | 4. **File remains in destination**   |

## Missing Files Script

If the linker was offline and events were missed, you can scan the source directory to find and link any missing files:

```bash
docker compose exec linker python missing_files.py
```
Note: The container must be running for this command to work.

# DONT USE THE compose.yml DIRECTLY

If you have Syncthing running already on the same host, you should integrate the linker into your existing setup as
described below.

## Prerequisites

An external docker network was created with the name "syncthing".

```bash
docker network create syncthing
```

### Example Syncthing Setup

Your Syncthing folders should ideally be organized under a common root, for example `files/source/*`.

.env:
```env
FILES_FOLDER=/mnt/Docker/Syncthing/files
```

docker-compose.yaml:
```yaml
networks:
  syncthing:
    external: true

volumes:
  files:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: ${FILES_FOLDER:-./files}

services:
  syncthing:
    image: lscr.io/linuxserver/syncthing:latest
    volumes:
      - /srv/Syncthing/config:/config
      - files:/files
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Berlin
    ports:
      - "8384:8384"
      - "22000:22000/tcp"
      - "22000:22000/udp"
      - "21027:21027/udp"
    restart: unless-stopped
    networks:
      - syncthing
```

## Installation

The linker needs the **Syncthing API key** to connect to the Syncthing server. This key can be found in the Syncthing web
interface under `Actions → Settings → API Key`.

![settings.png](images/settings.png)

Having the prerequisites in place, which follows the best practice for the `syncthing-linker`, the installation looks like this:

.env:
```env
FILES_FOLDER=/mnt/Docker/Syncthing/files
SYNCTHING_API_KEY=
```

docker-compose.yaml
```yaml
networks:
  syncthing:
    external: true

volumes:
  files:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: ${FILES_FOLDER:-./files}

services:
  linker:
    image: evoweb/syncthing-linker:${TAG:-latest}
    volumes:
      - files:/files
      # - ./config:/config #  Optional
    environment:
      PUID: 1000
      PGID: 1000
      TZ: Europe/Berlin
      SYNCTHING_HOST: "${SYNCTHING_HOST:-syncthing}"
      SYNCTHING_PORT: "${SYNCTHING_PORT:-8384}"
      SYNCTHING_API_KEY: "${SYNCTHING_API_KEY}"
      # SYNCTHING_HTTPS: "true" # Optional
      # SYNCTHING_CERT_FILE: "/path/to/cert" # Optional
    restart: unless-stopped
    networks:
      - syncthing
```

## Advanced Configuration

If you need a different folder structure, you can override the default configuration by mounting a config/config.yaml
file into the container.

config/config.yaml:
```yaml
# Paths are absolute inside the container
source: /files/source
destination: /files/destination

# Regex pattern for files to ignore
excludes: '\.tmp$|(?i)desktop\.ini'

# Comma-separated list of Syncthing events to listen to
# Default: ItemFinished
filter: ItemFinished,FolderSummary
```

### Folder Structure Example

Source and destination folders need to be relative to the base folder. The folder name must be the name of the
mount point in the container.

For example, this would be a good structure:
```
base-folder/
  target/
  shadow/
```

This would require that the config.yaml file looks like this:
```yaml
sources: /base-folder/target
destinations: /base-folder/shadow
```
And the docker-compose.yaml would look like this:
```yaml
services:
  linker:
    volumes:
      - base-folder:/base-folder
```

## Development

- for development start the container with `make development`.
- connect to it with `make connect`. By that the files in /app can be modified, and the changes will be reflected in the
running container.
- afterwards the container needs to be rebuilt with `make build`, to check if everything works as expected.

## Releasing

Pushing a new tag to the repository will trigger a new release to docker hub.
