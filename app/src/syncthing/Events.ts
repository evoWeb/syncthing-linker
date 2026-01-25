import BaseAPI from './BaseAPI';
import { RequestParameters } from './BaseAPI';
import ServiceConfig from './ServiceConfig';
import SyncthingException from './SyncthingException';

export interface EventData {
  action: string;
  error: string | null;
  folder?: string;
  item?: string;
  type?: string;
}

export interface Event {
  id: number;
  globalID: number;
  time: string;
  type: string;
  data: EventData;
}

export class Events extends BaseAPI {
  /**
   * HTTP REST endpoints for Event-based calls.
   *
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#event-endpoints
   *
   * Syncthing provides a simple long polling interface for exposing events
   * from the core utility towards a GUI.
   *
   * >>> l = logging.Logger()
   * >>> c = ServiceConfig(...)
   * >>> event_stream = Events(c, limit=5)
   */
  protected prefix = '/rest/';

  private readonly filters?: string[];
  private readonly limit: number;
  private _lastSeenId: number;
  private _count: number = 0;

  constructor(config: ServiceConfig, logger: Console, lastSeenId: number, filters?: string[], limit: number = 50) {
    super(config, logger);
    this._lastSeenId = lastSeenId;
    this.filters = filters;
    this.limit = limit;
  }

  /**
   * The number of events that have been processed by this event stream.
   */
  get count(): number {
    return this._count;
  }

  /**
   * The id of the last seen event.
   */
  get lastSeenId(): number {
    return this._lastSeenId;
  }

  /**
   * To receive events, perform an HTTP GET of /rest/events.
   *
   *                 To filter the event list, in effect, creating a specific subscription for only the
   *                 desired event types, add a parameter events=EventTypeA,EventTypeB,... where the event
   *                 types are any of the Event Types. If no filter is specified, all events except
   *                 LocalChangeDetected and RemoteChangeDetected are included.
   *
   *                 The optional parameter since=<lastSeenID> sets the ID of the last event you’ve already
   *                 seen. Syncthing returns a JSON encoded array of event objects, starting at the event
   *                 just after the one with this last seen ID. The default value is 0, which returns all
   *                 events. There is a limit to the number of events buffered, so if the rate of events is
   *                 high or the time between polling calls is long, some events might be missed. This can
   *                 be detected by noting a discontinuity in the event IDs.
   *
   *                 If no new events are produced since <lastSeenID>, the HTTP call blocks and waits for
   *                 new events to happen before returning. If <lastSeenID> is a future ID, the HTTP call
   *                 blocks until such ID is reached or timeouts. By default, it times out after 60 seconds
   *                 returning an empty array. The time-out duration can be customized with the optional
   *                 parameter timeout=<seconds>.
   *
   *                 To receive only a limited number of events, add the limit=<n> parameter with a
   *                 suitable value for n and only the last n events will be returned. This can be used
   *                 to catch up with the latest event ID after a disconnection, for example,
   *                 /rest/events?since=0&limit=1.
   *
   *                 Args:
   *                     using_url (str): REST HTTP endpoint
   *                     filters (List[str]): Creates an "event group" in Syncthing to
   *                         only receive events that have been subscribed to.
   *                     limit (int): The number of events to query in the history
   *                         to catch up to the current state.
   * @param usingUrl
   * @param filters
   * @param limit
   */
  async* events(
    usingUrl: string,
    filters: string[] | null = null,
    limit: number | null = null
  ): AsyncGenerator<Event> {
    const params: RequestParameters = {
      since: this.lastSeenId,
    };

    if (limit !== null) {
      params.limit = limit;
    }

    if (this.serviceConfig.timeout > 0) {
      params.timeout = this.serviceConfig.timeout;
    }

    if (filters && filters.length > 0) {
      params.events = filters.join(',');
    }

    try {
      const data = await this.get<Event[]>(usingUrl, undefined, undefined, params);
      if (data && data.length > 0) {
        for (const event of data) {
          this._count++;
          yield event;
        }
        this._lastSeenId = data[data.length - 1].id;
      }
    } catch (error) {
      throw new SyncthingException('Timeout while fetching new events', { cause: error });
    }
  }

  /**
   * This convenience endpoint provides the same event stream, but pre-filtered to show
   *                 only LocalChangeDetected and RemoteChangeDetected event types. The events parameter
   *                 is not used.
   */
  async* eventsDisk(): AsyncGenerator<Event> {
    yield* this.events('events/disk', null, this.limit);
  }

  /**
   * Helper interface for events.
   */
  async* [Symbol.asyncIterator](): AsyncGenerator<Event> {
    yield* this.events('events', this.filters || null, this.limit);
  }
}
