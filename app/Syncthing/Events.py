from requests.exceptions import Timeout
from urllib3.exceptions import TimeoutError
from typing import Generator

from .BaseAPI import BaseAPI
from .SyncthingError import SyncthingError
from .Utilities import string_types


NoneType = type(None)


class Events(BaseAPI):
    """ HTTP REST endpoints for Event-based calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#event-endpoints

        Syncthing provides a simple long polling interface for exposing events
        from the core utility towards a GUI.

        .. code-block:: python

           syncthing = Syncthing()
           event_stream = syncthing.events(limit=5)

           for event in event_stream:
               print(event)
               if event_stream.count > 10:
                   event_stream.stop()
    """

    prefix: str = '/rest/'

    def __init__(
        self,
        api_key,
        last_seen_id=None,
        filters=None,
        limit=None,
        *args,
        **kwargs
    ):
        if 'timeout' not in kwargs:
            # increase our timeout to account for long polling.
            # this will reduce the number of timed-out connections, which are
            # swallowed by the library anyway
            kwargs['timeout'] = 60.0  #seconds

        super(Events, self).__init__(api_key, *args, **kwargs)
        self._last_seen_id = last_seen_id or 0
        self._filters = filters
        self._limit = limit

        self._count = 0
        self.blocking = True

    @property
    def count(self) -> int:
        """ The number of events that have been processed by this event stream.

            Returns:
                int
        """
        return self._count

    @property
    def last_seen_id(self) -> int:
        """ The id of the last seen event.

            Returns:
                int
        """
        return self._last_seen_id

    def disk_events(self) -> Generator[dict]:
        """ Blocking generator of disk related events. Each event is represented as a ``dict`` with metadata.

            Returns:
                generator[dict]
        """
        for event in self._events('events/disk', None, self._limit):
            yield event

    def stop(self) -> None:
        """ Breaks the while-loop while the generator is polling for event changes.

            Returns:
                  None
        """
        self.blocking = False

    def _events(self, using_url, filters=None, limit=None) -> Generator[dict]:
        """ A long-polling method that queries Syncthing for events.

            Args:
                using_url (str): REST HTTP endpoint
                filters (List[str]): Creates an "event group" in Syncthing to
                    only receive events that have been subscribed to.
                limit (int): The number of events to query in the history
                    to catch up to the current state.

            Returns:
                generator[dict]
        """

        # coerce
        if not isinstance(limit, (int, NoneType)):
            limit = None

        # coerce
        if filters is None:
            filters = []

        # format our list into the correct expectation of string with commas
        if isinstance(filters, string_types):
            filters = filters.split(',')

        # reset the state if the loop was broken with `stop`
        if not self.blocking:
            self.blocking = True

        # block/long-poll for updates to the events api
        while self.blocking:
            params = {
                'since': self._last_seen_id,
                'limit': limit,
            }

            if filters:
                params['events'] = ','.join(map(str, filters))

            try:
                data = self.get(using_url, params=params, raw_exceptions=True)
            except (Timeout, TimeoutError):
                # swallow timeout errors for long polling
                data = None
            except Exception as e:
                raise SyncthingError('', e)

            if data:
                for event in data:
                    # handle potentially multiple events returned in a list
                    self._count += 1
                    yield event
                # update our last_seen_id to move our event counter forward
                last: dict = data[-1]
                self._last_seen_id = last['id']

    def __iter__(self) -> Generator[dict]:
        """ Helper interface for :obj:`._events` """
        for event in self._events('events', self._filters, self._limit):
            yield event
