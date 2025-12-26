import requests
import warnings

from .BaseAPI import BaseAPI
from .Utilities import ErrorEvent
from .Utilities import keys_to_datetime
from .Utilities import parse_datetime
from .Utilities import string_types

class System(BaseAPI):
    """ HTTP REST endpoint for System calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#system-endpoints
    """

    prefix = '/rest/system/'

    def browse(self, path=None) -> list[str]:
        """ Returns a list of directories matching the path given.

        Args:
            path (str): glob pattern.

        Returns:
            List[str]
        """
        params = None
        if path:
            assert isinstance(path, string_types)
            params = {'current': path}
        return self.get('browse', params=params)

    # DEPRECATED
    def config(self):
        """ Returns the current configuration.

            Returns:
                dict

            >>> s = syncthing_factory().system
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
    def set_config(self, config, and_restart=False):
        """ Post the full contents of the configuration in the same format as
        returned by:func:`.config`. The configuration will be saved to disk,
        and the ``configInSync`` flag set to ``False``. Restart Syncthing to
        activate."""
        assert isinstance(config, dict)
        self.post('config', data=config)
        if and_restart:
            self.restart()

    # DEPRECATED
    def config_insync(self):
        """ Returns whether the config is in sync, i.e. whether the running
            configuration is the same as that on disk.

            Returns:
                bool
        """
        status = self.get('config/insync').get('configInSync', False)
        if status is None:
            status = False
        return status

    def connections(self):
        """ Returns the list of configured devices and some metadata
            associated with them. The list also contains the local device
            itself as not connected.

            Returns:
                dict

            >>> s = syncthing_factory().system
            >>> connections = s.connections()
            >>> sorted([k for k in connections.keys()])
            ['connections', 'total']
            >>> isinstance(connections['connections'], dict)
            True
            >>> isinstance(connections['total'], dict)
            True
        """
        return self.get('connections')

    def debug(self):
        """ Returns the set of debug facilities and which of them are
            currently enabled.

            Returns:
                dict

            >>> s = syncthing_factory().system
            >>> debug = s.debug()
            >>> debug
            ... #doctest: +ELLIPSIS
            {...}
            >>> len(debug.keys())
            2
            >>> 'enabled' in debug and 'facilities' in debug
            True
            >>> isinstance(debug['enabled'], list) or debug['enabled'] is None
            True
            >>> isinstance(debug['facilities'], dict)
            True
        """
        return self.get('debug')

    def disable_debug(self, *on):
        """ Disables debugging for specified facilities.

            Args:
                on (str): debugging points to apply ``disable``.

            Returns:
                None
        """
        self.post('debug', params={'disable': ','.join(on)})

    def enable_debug(self, *on):
        """ Enables debugging for specified facilities.

            Args:
                on (str): debugging points to apply ``enable``.

            Returns:
                None
        """
        self.post('debug', params={'enable': ','.join(on)})

    def discovery(self):
        """ Returns the contents of the local discovery cache.

            Returns:
                dict
        """
        return self.get('discovery')

    def add_discovery(self, device, address):
        """ Add an entry to the discovery cache.

            Args:
                device (str): Device ID.
                address (str): destination address, a valid hostname or
                    IP address that's serving a Syncthing instance.

            Returns:
                None
        """
        self.post('discovery', params={'device': device,
                                       'address': address})

    def clear(self):
        """ Remove all recent errors.

            Returns:
                None
        """
        self.post('error/clear')


    def clear_errors(self):
        """ Alias function for :meth:`.clear`. """
        self.clear()

    def errors(self):
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

    def show_error(self, message):
        """ Send an error message to the active client. The new error will be
            displayed on any active GUI clients.

            Args:
                message (str): Plain-text message to display.

            Returns:
                None

            >>> s = syncthing_factory()
            >>> s.system.show_error('my error msg')
            >>> s.system.errors()[0]
            ... # doctest: +ELLIPSIS
            ErrorEvent(when=datetime.datetime(...), message='my error msg')
            >>> s.system.clear_errors()
            >>> s.system.errors()
            []
        """
        assert isinstance(message, string_types)
        self.post('error', data=message)

    def log(self):
        """ Returns the list of recent log entries.

            Returns:
                dict
        """
        return self.get('log')

    def pause(self, device):
        """ Pause the given device.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        resp = self.post('pause', params={'device': device},
                         return_response=True)
        error = resp.text
        if not error:
            error = None
        return {'success': resp.status_code == requests.codes.ok,
                'error': error}

    def ping(self, with_method='GET'):
        """ Pings the Syncthing server.

            Args:
                with_method (str): uses a given HTTP method, options are
                    ``GET`` and ``POST``.

            Returns:
                dict
        """
        assert with_method in ('GET', 'POST')
        if with_method == 'GET':
            return self.get('ping')
        return self.post('ping')

    def reset(self):
        """ Erase the current index database and restart Syncthing.

            Returns:
                None
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={})

    def reset_folder(self, folder):
        """ Erase the database index from a given folder and restart Syncthing.

            Args:
                folder (str): Folder ID.

            Returns:
                None
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={}, params={'folder': folder})

    def restart(self):
        """ Immediately restart Syncthing.

            Returns:
                None
        """
        self.post('restart', data={})

    def resume(self, device):
        """ Resume the given device.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        resp = self.post('resume', params={'device': device},
                         return_response=True)
        error = resp.text
        if not error:
            error = None
        return {'success': resp.status_code == requests.codes.ok,
                'error': error}

    def shutdown(self):
        """ Causes Syncthing to exit and not restart.

            Returns:
                None
        """
        self.post('shutdown', data={})

    def status(self):
        """ Returns information about current system status and resource usage.

            Returns:
                dict
        """
        resp = self.get('status')
        resp = keys_to_datetime(resp, 'startTime')
        return resp

    def upgrade(self):
        """ Checks for a possible upgrade and returns an object describing
            the newest version and upgrade possibility.

            Returns:
                dict
        """
        return self.get('upgrade')

    def can_upgrade(self):
        """ Returns when there's a newer version than the instance running.

            Returns:
                bool
        """
        return (self.upgrade() or {}).get('newer', False)

    def do_upgrade(self):
        """ Perform an upgrade to the newest released version and restart.
            Does nothing if there is no newer version than currently running.

            Returns:
                None
        """
        return self.post('upgrade')

    def version(self):
        """ Returns the current Syncthing version information.

            Returns:
                dict
        """
        return self.get('version')