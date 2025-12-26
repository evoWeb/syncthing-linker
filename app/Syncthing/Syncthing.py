#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Based on the work of Blake VandeMerwe https://github.com/blakev/python-syncthing
# <<

import os
import logging

from collections import namedtuple
from dateutil.parser import parse as dateutil_parser

from Database import Database
from Events import Events
from Misc import Misc
from Statistics import Statistics
from SyncthingError import SyncthingError
from System import System


string_types = (str,)
logger = logging.getLogger(__name__)


DEFAULT_TIMEOUT = 10.0


ErrorEvent = namedtuple('ErrorEvent', 'when, message')
"""tuple[datetime.datetime,str]: used to process error lists more easily, 
instead of by two-key dictionaries. """

def initialize_syncthing():
    key = os.getenv('SYNCTHING_API_KEY')
    host = os.getenv('SYNCTHING_HOST', '127.0.0.1')
    port = os.getenv('SYNCTHING_PORT', 8384)
    is_https = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
    ssk_cert_file = os.getenv('SYNCTHING_CERT_FILE')
    return Syncthing(key, host, port, 10.0, is_https, ssk_cert_file)


def keys_to_datetime(obj, *keys):
    """ Converts all the keys in an object to DateTime instances.

        Args:
            obj (dict): the JSON-like ``dict`` object to modify inplace.
            keys (str): keys of the object being converted into DateTime
                instances.

        Returns:
            dict: ``obj`` inplace.

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
        if not isinstance(v, string_types):
            continue
        obj[k] = parse_datetime(v)
    return obj


def parse_datetime(s, **kwargs):
    """ Converts a time-string into a valid
    :py:class:`~datetime.datetime.DateTime` object.

        Args:
            s (str): string to be formatted.

        ``**kwargs`` is passed directly to :func:`.dateutil_parser`.

        Returns:
            :py:class:`~datetime.datetime.DateTime`
    """
    if not s:
        return None
    try:
        ret = dateutil_parser(s, **kwargs)
    except (OverflowError, TypeError, ValueError) as e:
        raise SyncthingError('datetime parsing error from %s' % s, e)
    return ret


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
            system: instance of :class:`.System`.
            database: instance of :class:`.Database`.
            stats: instance of :class:`.Statistics`.
            misc: instance of :class:`.Misc`.

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
        self.misc = Misc(api_key, **kwargs)

    def events(self, last_seen_id=None, filters=None, **kwargs):
        kw = dict(self.__kwargs)
        kw.update(kwargs)
        return Events(api_key=self.__api_key,
                      last_seen_id=last_seen_id,
                      filters=filters,
                      **kw)


__all__ = [
    'ErrorEvent',
    'initialize_syncthing',
    'keys_to_datetime',
    'parse_datetime',
    'string_types',
    'Syncthing'
]

if __name__ == "__main__":
    import doctest
    doctest.testmod()