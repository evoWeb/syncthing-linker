from collections import namedtuple
from dateutil.parser import parse as dateutil_parser

from .SyncthingError import SyncthingError

string_types = (str,)


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


ErrorEvent = namedtuple('ErrorEvent', 'when, message')
"""tuple[datetime.datetime,str]: used to process error lists more easily, 
instead of by two-key dictionaries. """

__all__ = [
    'ErrorEvent',
    'keys_to_datetime',
    'parse_datetime',
    'string_types'
]