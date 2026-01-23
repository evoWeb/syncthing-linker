#!/bin/sh

PUID=${PUID:-1000}
PGID=${PGID:-1000}

# Check if group with PGID exists, create if not
if ! getent group ${PGID} >/dev/null; then
    addgroup -g ${PGID} appgroup
fi

# Check if user with PUID exists, create if not
if ! getent passwd ${PUID} >/dev/null; then
    # Get the group name for PGID
    GROUP_NAME=$(getent group ${PGID} | cut -d: -f1)
    adduser -D -u ${PUID} -G ${GROUP_NAME} appuser
fi

# Get the username for PUID
USER_NAME=$(getent passwd ${PUID} | cut -d: -f1)

# Fix ownership of app directories
chown -R ${PUID}:${PGID} /usr/src/app /config

# Drop privileges and run as the user
exec su-exec ${USER_NAME} "$@"