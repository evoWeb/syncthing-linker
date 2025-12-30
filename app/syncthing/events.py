from requests.exceptions import Timeout
from urllib3.exceptions import TimeoutError
from typing import Generator

from .base_api import BaseAPI
from .syncthing_exception import SyncthingException


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
                   del event_stream
    """

    prefix: str = '/rest/'

    def __init__(
        self,
        api_key: str,
        last_seen_id: int = None,
        filters: list[str] = None,
        limit: int = 10,
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

    def events(
        self,
        using_url: str,
        filters: list[str] | None = None,
        limit: int | None = None
    ) -> Generator[dict]:
        """ To receive events, perform an HTTP GET of /rest/events.

            To filter the event list, in effect, creating a specific subscription for only the
            desired event types, add a parameter events=EventTypeA,EventTypeB,... where the event
            types are any of the Event Types. If no filter is specified, all events except
            LocalChangeDetected and RemoteChangeDetected are included.

            The optional parameter since=<lastSeenID> sets the ID of the last event you’ve already
            seen. Syncthing returns a JSON encoded array of event objects, starting at the event
            just after the one with this last seen ID. The default value is 0, which returns all
            events. There is a limit to the number of events buffered, so if the rate of events is
            high or the time between polling calls is long, some events might be missed. This can
            be detected by noting a discontinuity in the event IDs.

            If no new events are produced since <lastSeenID>, the HTTP call blocks and waits for
            new events to happen before returning. If <lastSeenID> is a future ID, the HTTP call
            blocks until such ID is reached or timeouts. By default, it times out after 60 seconds
            returning an empty array. The time-out duration can be customized with the optional
            parameter timeout=<seconds>.

            To receive only a limited number of events, add the limit=<n> parameter with a
            suitable value for n and only the last n events will be returned. This can be used
            to catch up with the latest event ID after a disconnection, for example,
            /rest/events?since=0&limit=1.

            Args:
                using_url (str): REST HTTP endpoint
                filters (List[str]): Creates an "event group" in Syncthing to
                    only receive events that have been subscribed to.
                limit (int): The number of events to query in the history
                    to catch up to the current state.
        """

        # coerce
        if not isinstance(limit, (int, None)):
            limit = None

        # coerce
        if filters is None:
            filters = []

        # block/long-poll for updates to the events api
        while True:
            params: dict[str, str | int] = {
                'since': self._last_seen_id,
                'limit': limit,
            }

            if filters:
                params['events'] = ','.join(filters)

            try:
                data = self.get(using_url, params=params, raw_exceptions=True)
            except (Timeout, TimeoutError):
                # swallow timeout errors for long polling
                data = None
            except Exception as e:
                raise SyncthingException('', e)

            if data:
                for event in data:
                    # handle potentially multiple events returned in a list
                    self._count += 1
                    yield event
                # update our last_seen_id to move our event counter forward
                last: dict = data[-1]
                self._last_seen_id = last.get('id')

    def events_disk(self) -> Generator[dict]:
        """ This convenience endpoint provides the same event stream, but pre-filtered to show
            only LocalChangeDetected and RemoteChangeDetected event types. The events parameter
            is not used.
        """
        for event in self.events('events/disk', None, self._limit):
            yield event

    @property
    def count(self) -> int:
        """ The number of events that have been processed by this event stream. """
        return self._count

    @property
    def last_seen_id(self) -> int:
        """ The id of the last seen event. """
        return self._last_seen_id

    def __iter__(self) -> Generator[dict]:
        """ Helper interface for :obj:`._events` """
        yield from self.events('events', self._filters, self._limit)

__all__ = [
    'Events'
]