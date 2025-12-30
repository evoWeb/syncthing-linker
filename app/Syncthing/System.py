import datetime
import requests
import warnings

from collections import namedtuple
from dateutil.parser import parse as dateutil_parser

from .BaseAPI import BaseAPI
from .SyncthingException import SyncthingException


ErrorEvent = namedtuple('ErrorEvent', 'when, message')
""" tuple[datetime.datetime,str]: used to process error lists more easily, instead of by two-key dictionaries. """


def keys_to_datetime(obj: dict | None, *keys) -> dict:
    """ Converts all the keys in an object to DateTime instances.

        Args:
            obj (dict): the JSON-like ``dict`` object to modify inplace.
            keys (str): keys of the object being converted into DateTime
                instances.

        >>> keys_to_datetime(None) is None
        True
        >>> keys_to_datetime({})
        {}
        >>> a = {}
        >>> id(keys_to_datetime(a)) == id(a)
        True
        >>> a = {'one': '2016-06-06T19:41:43.039284',
                 'two': '2016-06-06T19:41:43.039284'}
        >>> keys_to_datetime(a) == a
        True
        >>> keys_to_datetime(a, 'one')['one']
        datetime.datetime(2016, 6, 6, 19, 41, 43, 39284)
        >>> keys_to_datetime(a, 'one')['two']
        '2016-06-06T19:41:43.039284'
    """
    if not keys:
        return obj
    for k in keys:
        if k not in obj:
            continue
        v = obj[k]
        if not isinstance(v, str):
            continue
        obj[k] = parse_datetime(v)
    return obj


def parse_datetime(date_string: str | None, **kwargs) -> datetime.datetime | None:
    """ Converts a time-string into a valid :py:class:`~datetime.datetime.DateTime` object.

        Args:
            date_string (str): string to be formatted.

        ``**kwargs`` is passed directly to :func:`.dateutil_parser`.
    """
    if not date_string:
        return None
    try:
        ret = dateutil_parser(date_string, **kwargs)
    except (OverflowError, TypeError, ValueError) as e:
        raise SyncthingException('datetime parsing error from %s' % date_string, e)
    return ret


class System(BaseAPI):
    """ HTTP REST endpoint for System calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#system-endpoints
    """

    prefix = '/rest/system/'

    def browse(self, path: str | None = None) -> list[str]:
        """ Returns a list of directories matching the path given by the optional parameter current.
            The path can use patterns as described in Go’s filepath package. A ‘*’ will always be
            appended to the given path (e.g. /tmp/ matches all its subdirectories). If the option
            currently is not given, filesystem root paths are returned.

        Args:
            path (str): glob pattern.
        """
        params = None
        if path:
            assert isinstance(path, str)
            params = {'current': path}
        return self.get('browse', params=params)

    # DEPRECATED
    def config(self) -> dict:
        """ Deprecated since the version v1.12.0: This endpoint still works as before but is
            deprecated. Use /rest/config instead.

            Returns the current configuration.

            >>> s = Syncthing.create_instance().system
            >>> config = s.config()
            >>> config
            ... # doctest: +ELLIPSIS
            {...}
            >>> 'version' in config and config['version'] >= 15
            True
            >>> 'folders' in config
            True
            >>> 'devices' in config
            True
        """
        return self.get('config')

    # DEPRECATED
    def set_config(self, config: dict, and_restart = False) -> None:
        """ Deprecated since the version v1.12.0: This endpoint still works as before but is
            deprecated. Use Config Endpoints instead.

            Post the full contents of the configuration in the same format as returned by the
            corresponding GET request. When posting the configuration succeeds, the posted
            configuration is immediately applied, except for changes that require a restart.
            Query /rest/config/restart-required to check if a restart is required.

            This endpoint is the main point to control Syncthing, even if the change only concerns
            a very small part of the config: The usual workflow is to get the config, modify the
            necessary parts and post it again.
        """
        assert isinstance(config, dict)
        self.post('config', data=config)
        if and_restart:
            self.restart()

    # DEPRECATED
    def config_insync(self) -> bool:
        """ Deprecated since the version v1.12.0: This endpoint still works as before but is
            deprecated. Use /rest/config/restart-required instead.

            Returns whether the config is in sync, i.e. whether the running configuration is
            the same as that on disk.
        """
        status = self.get('config/insync').get('configInSync', False)
        if status is None:
            status = False
        return status

    def connections(self) -> dict:
        """ Returns the list of configured devices and some metadata associated with them.

            The connection types are tcp-client, tcp-server, relay-client, relay-server,
            quic-client and quic-server.

            >>> s = Syncthing.create_instance().system
            >>> connections = s.connections()
            >>> sorted([k for k in connections.keys()])
            ['connections', 'total']
            >>> isinstance(connections['connections'], dict)
            True
            >>> isinstance(connections['total'], dict)
            True
        """
        return self.get('connections')

    def discovery(self) -> dict:
        """ Returns the contents of the local discovery cache. """
        return self.get('discovery')

    def add_discovery(self, device: str, address: str) -> None:
        """ Post with the query parameters device and addr to add entries to the discovery cache.

            Args:
                device (str): Device ID.
                address (str): destination address, a valid hostname or
                    IP address that's serving a Syncthing instance.
        """
        self.post('discovery', params={'device': device, 'address': address})

    def clear(self) -> None:
        """ Post with an empty body to remove all recent errors. """
        self.post('error/clear')

    def clear_errors(self) -> None:
        """ Alias function for :meth:`.clear`. """
        self.clear()

    def errors(self) -> list[ErrorEvent]:
        """ Returns the list of recent errors.

            Returns:
                list: of :obj:`.ErrorEvent` tuples.
        """
        ret_errs = list()
        errors = self.get('error').get('errors', None) or list()
        assert isinstance(errors, list)
        for err in errors:
            when = parse_datetime(err.get('when', None))
            msg = err.get('message', '')
            e = ErrorEvent(when, msg)
            ret_errs.append(e)
        return ret_errs

    def add_error(self, message: str) -> None:
        """ Post with an error message in the body (plain text) to register a new error. The new
            error will be displayed on any active GUI clients.

            Args:
                message (str): Plain-text message to display.

            >>> s = Syncthing.create_instance()
            >>> s.system.show_error('my error msg')
            >>> s.system.errors()[0]
            ... # doctest: +ELLIPSIS
            ErrorEvent(when=datetime.datetime(...), message='my error msg')
            >>> s.system.clear_errors()
            >>> s.system.errors()
            []
        """
        assert isinstance(message, str)
        self.post('error', data=message)

    def log(self) -> dict:
        """ Returns the list of recent log entries. The optional since parameter limits the results
            to a message newer than the given timestamp in RFC 3339 format.
        """
        return self.get('log')

    def loglevels(self) -> dict:
        """ Returns the set of log facilities and their current log level. """
        return self.get('loglevels')

    def set_loglevels(self, facility: str, level: str) -> None:
        """ Returns the set of log facilities and their current log level.

            Args:
                facility (str): Facility to set.
                level (str): Level to set.
        """
        self.post('loglevels', data={facility: level})

    def paths(self) -> dict:
        """ Returns the path locations used internally for storing configuration, database, and others. """
        return self.get('paths')

    def pause(self, device: str) -> dict:
        """ Pause the given device or all devices.

            Takes the optional parameter device (device ID). When omitted, pauses all devices.
            Returns status 200 and no content upon success, or status 500 and a plain text error
            on failure.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        response = self.post('pause', params={'device': device}, return_response=True)
        error = response.text
        if not error:
            error = None
        return {'success': response.status_code == requests.codes.ok, 'error': error}

    def ping(self, method: str = 'GET') -> dict:
        """ Returns a {"ping": "pong"} object.

            Args:
                method (str): uses a given HTTP method, options are ``GET`` and ``POST``.
        """
        assert method in ('GET', 'POST')
        if method == 'GET':
            return self.get('ping')
        return self.post('ping')

    def reset(self) -> None:
        """ Post with an empty body to erase the current index database and restart Syncthing. With
            no query parameters, the entire database is erased from the disk. By specifying the
            folder parameter with a valid folder ID, only information for that folder will be erased
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={})

    def reset_folder(self, folder: str) -> None:
        """ Post with an empty body to erase the current index database and restart Syncthing. With
            no query parameters, the entire database is erased from the disk. By specifying the
            folder parameter with a valid folder ID, only information for that folder will be erased

            Args:
                folder (str): Folder ID.
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={}, params={'folder': folder})

    def restart(self) -> None:
        """ Post with an empty body to immediately restart Syncthing. """
        self.post('restart')

    def resume(self, device: str | None = None) -> dict:
        """ Resume the given device or all devices.

            Takes the optional parameter device (device ID). When omitted, resumes all devices.
            Returns status 200 and no content upon success, or status 500 and a plain text error
            on failure.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        if device is None:
            resp = self.post('resume', return_response=True)
        else:
            resp = self.post('resume', params={'device': device}, return_response=True)

        error = resp.text
        if not error:
            error = None
        return {'success': resp.status_code == requests.codes.ok, 'error': error}

    def shutdown(self) -> None:
        """ Post with an empty body to cause Syncthing to exit and not restart. """
        self.post('shutdown')

    def status(self) -> dict:
        """ Returns information about current system status and resource usage. The CPU percent
            value has been deprecated from the API and will always report 0.
        """
        resp = self.get('status')
        resp = keys_to_datetime(resp, 'startTime')
        return resp

    def upgrade(self) -> dict:
        """ Checks for a possible upgrade and returns an object describing the newest version
            and upgrade possibility.
        """
        return self.get('upgrade')

    def can_upgrade(self) -> bool:
        """ Returns when there's a newer version than the instance running. """
        return (self.upgrade() or {}).get('newer', False)

    def do_upgrade(self) -> None:
        """ Perform an upgrade to the newest released version and restart. Does nothing if there
            is no newer version than currently running.
        """
        self.post('upgrade')

    def version(self) -> dict:
        """ Returns the current Syncthing version information. """
        return self.get('version')

__all__ = [
    'ErrorEvent',
    'keys_to_datetime',
    'parse_datetime',
    'System'
]