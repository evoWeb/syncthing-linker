#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Based on the work of Blake VandeMerwe https://github.com/blakev/python-syncthing
# <<

import os

from .Database import Database
from .Events import Events
from .Service import Service
from .Statistics import Statistics
from .System import System


DEFAULT_TIMEOUT = 10.0


def syncthing_factory():
    key = os.getenv('SYNCTHING_API_KEY')
    host = os.getenv('SYNCTHING_HOST', '127.0.0.1')
    port = os.getenv('SYNCTHING_PORT', 8384)
    is_https = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
    ssk_cert_file = os.getenv('SYNCTHING_CERT_FILE')
    return Syncthing(key, host, port, 10.0, is_https, ssk_cert_file)


class Syncthing(object):
    """ Default interface for interacting with Syncthing server instance.

        Args:
            api_key (str)
            host (str)
            port (int)
            timeout (float)
            is_https (bool)
            ssl_cert_file (str)

        Attributes:
            system: instance of :class:`System`.
            database: instance of :class:`Database`.
            stats: instance of :class:`Statistics`.
            service: instance of :class:`Service`.

        Note:
            - attribute :attr:`.db` is an alias of :attr:`.database`
            - attribute :attr:`.sys` is an alias of :attr:`.system`
    """

    def __init__(self, api_key, host='localhost', port=8384,
                 timeout=DEFAULT_TIMEOUT, is_https=False, ssl_cert_file=None):

        # save this for deferred api sub instances
        self.__api_key = api_key

        self.api_key = api_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.is_https = is_https
        self.ssl_cert_file = ssl_cert_file

        self.__kwargs = kwargs = {
            'host': host,
            'port': port,
            'timeout': timeout,
            'is_https': is_https,
            'ssl_cert_file': ssl_cert_file
        }

        self.system = self.sys = System(api_key, **kwargs)
        self.database = self.db = Database(api_key, **kwargs)
        self.stats = Statistics(api_key, **kwargs)
        self.service = Service(api_key, **kwargs)

    def events(self, last_seen_id=None, filters=None, **kwargs):
        kw = dict(self.__kwargs)
        kw.update(kwargs)
        return Events(api_key=self.__api_key, last_seen_id=last_seen_id, filters=filters, **kw)


__all__ = [
    'syncthing_factory',
    'Syncthing'
]

if __name__ == "__main__":
    import doctest
    doctest.testmod()