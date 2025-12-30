#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Based on the work of Blake VandeMerwe https://github.com/blakev/python-syncthing
# <<

import os

from .base_api import DEFAULT_TIMEOUT
from .cluster import Cluster
from .config import Config
from .database import Database
from .debug import Debug
from .events import Events
from .noauth import Noauth
from .service import Service
from .statistics import Statistics
from .system import System


class Syncthing:
    """ Default interface for interacting with Syncthing server instance.

        Wrapping all endpoints described in https://docs.syncthing.net/dev/rest.html

        Attributes:
            cluster: instance of `Cluster`.
            config: instance of `Config`.
            database: instance of `Database`.
            debug: instance of `Debug`.
            noauth: instance of `Noauth`.
            system: instance of `System`.
            statistics: instance of `Statistics`.
            service: instance of `Service`.
    """

    _api_key: str
    _host: str
    _port: int
    _timeout: int
    _is_https: bool
    _ssl_cert_file: str
    _kwargs: dict

    def __init__(
        self,
        api_key: str,
        host: str = 'localhost',
        port: int = 8384,
        timeout: int = DEFAULT_TIMEOUT,
        is_https: bool = False,
        ssl_cert_file: str | None = None
    ):
        self._api_key = api_key
        self._host = host
        self._port = port
        self._timeout = timeout
        self._is_https = is_https
        self._ssl_cert_file = ssl_cert_file

        self._kwargs = kwargs = {
            'host': host,
            'port': port,
            'timeout': timeout,
            'is_https': is_https,
            'ssl_cert_file': ssl_cert_file
        }

        self.cluster = Cluster(api_key, **kwargs)
        self.config = Config(api_key, **kwargs)
        self.database = Database(api_key, **kwargs)
        self.debug = Debug(api_key, **kwargs)
        self.noauth = Noauth(api_key, **kwargs)
        self.service = Service(api_key, **kwargs)
        self.statistics = Statistics(api_key, **kwargs)
        self.system = System(api_key, **kwargs)

    def events(self, last_seen_id: int | None = None, filters: list[str] | None = None, **kwargs):
        kw = dict(self._kwargs)
        kw.update(kwargs)
        return Events(api_key=self._api_key, last_seen_id=last_seen_id, filters=filters, **kw)

    @classmethod
    def create_instance(cls, key: str = None):
        return Syncthing(
            api_key=key if key != '' else os.getenv('SYNCTHING_API_KEY'),
            host=os.getenv('SYNCTHING_HOST', '127.0.0.1'),
            port=os.getenv('SYNCTHING_PORT', 8384),
            timeout=10,
            is_https=os.getenv('SYNCTHING_HTTPS', '0').lower() in ('1', 'true', 'yes'),
            ssl_cert_file=os.getenv('SYNCTHING_CERT_FILE')
        )

if __name__ == '__main__':
    import doctest
    doctest.testmod()