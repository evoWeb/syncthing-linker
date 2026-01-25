import BaseAPI from './BaseAPI';
import { RequestData, RequestParameters } from './BaseAPI';

class ErrorEvent {
  /**
   * used to process error lists more easily, instead of by two-key dictionaries.
   */
  public when: Date | null;
  public message: string;

  constructor(when: Date | null, message: string) {
    this.when = when;
    this.message = message;
  }
}

interface SystemConfig {
  version: number;
  folders: { id: string }[];
  devices: { deviceID: string }[];
}

interface Connection {
  address: string;
  at: string;
  clientVersion: string;
  connected: boolean;
  inBytesTotal: number;
  isLocal: boolean;
  outBytesTotal: number;
  paused: boolean;
  startedAt: string;
  type: string;
}

interface SystemConnections {
  connections: Record<string, Connection>;
  total: {
    at: string;
    inBytesTotal: number;
    outBytesTotal: number;
  };
}

/**
 * Converts all the keys in an object to DateTime instances.
 *
 *         Args:
 *             object (dict): the JSON-like ``dict`` object to modify inplace.
 *             keys (str): keys of the object being converted into DateTime
 *                 instances.
 *
 *         >>> keysToDatetime(None) is None
 *         True
 *         >>> keysToDatetime({})
 *         {}
 *         >>> obj = {}
 *         >>> id(keysToDatetime(a)) == id(a)
 *         True
 *         >>> a = {'one': '2016-06-06T19:41:43.039284', 'two': '2016-06-06T19:41:43.039284'}
 *         >>> keysToDatetime(obj) == a
 *         True
 *         >>> keysToDatetime(obj, 'one').get('one')
 *         datetime.datetime(2016, 6, 6, 19, 41, 43, 39284)
 *         >>> keysToDatetime(obj, 'one').get('two')
 *         '2016-06-06T19:41:43.039284'
 *
 * @param object the JSON-like object to modify.
 * @param keys keys of the object being converted into Date instances.
 */
function keysToDatetime<T extends Record<string, Date | null | string | number>>(object: T, ...keys: (keyof T)[]): T {
  if (!object || keys.length === 0) {
    return object;
  }

  if (typeof object === 'object') {
    for (const key of keys) {
      if (!(key in object)) {
        continue;
      }
      const value = object[key];
      if (typeof value !== 'string') {
        continue;
      }
      object[key] = parseDatetime(value) as T[keyof T];
    }
  }

  return object;
}

/**
 * Converts a time-string into a valid :py:class:`~datetime.datetime.DateTime` object.
 *
 *         Args:
 *             date_string (str): string to be formatted.
 *
 *         ``**kwargs`` is passed directly to:func:`.parse`.
 *
 * @param dateString string to be formatted.
 */
function parseDatetime(dateString: string): Date | null {
  if (!dateString) {
    return null;
  }
  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    throw new Error(`datetime parsing error from ${dateString}`);
  }
  return date;
}

function isKeyOfRequestData(key: string, obj: RequestData): key is keyof RequestData {
  return key in obj;
}

export default class System extends BaseAPI {
  /**
   * HTTP REST endpoint for System calls.
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#system-endpoints
   */
  protected prefix = '/rest/system/';

  /**
   * Returns a list of directories matching the path given by the optional parameter current.
   *             The path can use patterns as described in Go’s filepath package. A ‘*’ will always be
   *             appended to the given path (e.g. /tmp/ matches all its subdirectories). If the option
   *             currently is not given, filesystem root paths are returned.
   *
   *         Args:
   *             path (str): glob pattern.
   * @param path
   */
  browse(path: string | undefined = undefined): Promise<string[]> {
    const params: RequestParameters|undefined = path !== undefined ? { current: path } : undefined;
    return this.get('browse', undefined, undefined, params);
  }

  /**
   * Deprecated since the version v1.12.0: This endpoint still works as before but is
   *             deprecated. Use /rest/config instead.
   *
   *             Returns the current configuration.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = System(c)
   *             >>> config = s.config()
   *             >>> config
   *             ... # doctest: +ELLIPSIS
   *             {...}
   *             >>> 'version' in config and config.get('version') >= 15
   *             True
   *             >>> 'folders' in config
   *             True
   *             >>> 'devices' in config
   *             True
   */
  config(): Promise<SystemConfig> {
    this.logger.warn('System.config() is deprecated: Use Config instead.');
    return this.get('config');
  }

  /**
   * Deprecated since the version v1.12.0: This endpoint still works as before but is
   *             deprecated. Use Config Endpoints instead.
   *
   *             Post the full contents of the configuration in the same format as returned by the
   *             corresponding GET request. When posting the configuration succeeds, the posted
   *             configuration is immediately applied, except for changes that require a restart.
   *             Query /rest/config/restart-required to check if a restart is required.
   *
   *             This endpoint is the main point to control Syncthing, even if the change only concerns
   *             a very small part of the config: The usual workflow is to get the config, modify the
   *             necessary parts and post it again.
   */
  setConfig(config: RequestData, andRestart: boolean = false): void {
    this.logger.warn('System.setConfig() is deprecated: Use Config.restartRequired instead.');
    this.post('config', config).then(() => {
      if (andRestart) {
        this.restart();
      }
    });
  }

  /**
   * Deprecated since the version v1.12.0: This endpoint still works as before but is
   *             deprecated. Use /rest/config/restart-required instead.
   *
   *             Returns whether the config is in sync, i.e. whether the running configuration is
   *             the same as that on disk.
   */
  async configInsync(): Promise<boolean> {
    this.logger.warn('System.configInsync() is deprecated: Use Config.restartRequired instead.');
    const response = await this.get<{ configInSync: boolean }>('config/insync');
    return (response.configInSync || false);
  }

  /**
   * Returns the list of configured devices and some metadata associated with them.
   *
   *             The connection types are tcp-client, tcpserver, relay-client, relay-server,
   *             quic-client, and quic-server.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = System(c)
   *             >>> connections = s.connections()
   *             >>> sorted([k for k in connections.keys()])
   *             ['connections', 'total']
   *             >>> isinstance(connections.get('connections'), dict)
   *             True
   *             >>> isinstance(connections.get('total'), dict)
   *             True
   */
  connections(): Promise<SystemConnections> {
    return this.get('connections');
  }

  /**
   * Returns the contents of the local discovery cache.
   */
  discovery(): Promise<Record<string, string[]>> {
    return this.get('discovery');
  }

  /**
   * Post with the query parameters device and addr to add entries to the discovery cache.
   *
   *             Args:
   *                 device (str): Device ID.
   *                 address (str): destination address, a valid hostname or
   *                     IP address that's serving a Syncthing instance.
   * @param deviceID
   * @param address
   */
  addDiscovery(deviceID: string, address: string): void {
    this.post('discovery', undefined, undefined, { device: deviceID, address: address });
  }

  /**
   * Post with an empty body to remove all recent errors.
   */
  clear(): void {
    this.post('error/clear');
  }

  /**
   * Alias function for :meth:`.clear`.
   */
  clearErrors(): void {
    this.clear();
  }

  /**
   * Returns the list of recent errors.
   *
   *             Returns:
   *                 list: of :obj:`.ErrorEvent` instances.
   */
  async errors(): Promise<ErrorEvent[]> {
    const response = await this.get<{ errors: { when: string, message: string }[] }>('error');
    const errors = response.errors || [];
    const result: ErrorEvent[] = [];
    errors.map((error: { when: string, message: string }) => {
      const when = parseDatetime(error.when);
      const message = error.message || '';
      result.push(new ErrorEvent(when, message));
    });
    return result;
  }

  /**
   * Post with an error message in the body (plain text) to register a new error. The new
   *             error will be displayed on any active GUI clients.
   *
   *             Args:
   *                 message (str): Plain-text message to display.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = System(c)
   *             >>> s.add_error('my error msg')
   *             >>> s.errors()[0]
   *             ... # doctest: +ELLIPSIS
   *             ErrorEvent(when=datetime.datetime(...), message='my error msg')
   *             >>> s.clear_errors()
   *             >>> s.errors()
   *             []
   * @param message
   */
  addError(message: string): void {
    this.post('error', { message: message });
  }

  /**
   * Returns the list of recent log entries. The optional since parameter limits the results
   *             to a message newer than the given timestamp in RFC 3339 format.
   */
  log(): Promise<{ messages: { when: string, message: string }[] }> {
    return this.get('log');
  }

  /**
   * Returns the set of log facilities and their current log level.
   */
  loglevels(): Promise<{ levels: Record<string, string>, packages: Record<string, string> }> {
    return this.get('loglevels');
  }

  /**
   * Returns the set of log facilities and their current log level.
   *
   *             Args:
   *                 facility (str): Facility to set.
   *                 level (str): Level to set.
   *
   * @param facility Facility to set.
   * @param level Level to set.
   */
  setLoglevels(facility: string, level: string): void {
    let data = undefined;
    if (isKeyOfRequestData(facility, {} as RequestData)) {
      data = { [facility]: level };
    }
    this.post('loglevels', data);
  }

  /**
   * Returns the path locations used internally for storing configuration, database, and others.
   */
  paths(): Promise<Record<string, string>> {
    return this.get('paths');
  }

  /**
   * Pause the given device or all devices.
   *
   *             Takes the optional parameter device (device ID). When omitted, pauses all devices.
   *             Returns status 200 and no content upon success, or status 500 and a plain text error
   *             on failure.
   *
   *             Args:
   *                 device (str): Device ID.
   *
   *             Returns:
   *                 dict: with keys ``success`` and ``error``.
   * @param device
   */
  async pause(device: string): Promise<{ success: boolean, error: string | null }> {
    try {
      await this.post('pause', undefined, undefined, { device: device });
      return { success: true, error: null };
      /* eslint-disable @typescript-eslint/no-explicit-any */
    } catch (error: any) {
      return { success: false, error: error.message || 'Unknown error' };
    }
  }

  /**
   * Returns a {"ping": "pong"} object.
   *
   *             Args:
   *                 method (str): uses a given HTTP method, options are ``GET`` and ``POST``.
   */
  async ping(method: string = 'GET'): Promise<{ ping: string }> {
    if (method !== 'GET' && method !== 'POST') {
      throw new Error(`Assertion failed: method must be either 'GET' or 'POST', got ${method} instead.`);
    }
    if (method === 'GET') {
      return this.get('ping');
    }
    return this.post('ping');
  }

  /**
   * Post with an empty body to erase the current index database and restart Syncthing. With
   *             no query parameters, the entire database is erased from the disk. By specifying the
   *             folder parameter with a valid folder ID, only information for that folder will be erased
   */
  reset(): void {
    this.logger.warn('This is a destructive action that cannot be undone.');
    this.post('reset', {});
  }

  /**
   * Post with an empty body to erase the current index database and restart Syncthing. With
   *             no query parameters, the entire database is erased from the disk. By specifying the
   *             folder parameter with a valid folder ID, only information for that folder will be erased
   *
   *             Args:
   *                 folder (str): Folder ID.
   * @param folder
   */
  resetFolder(folder: string): void {
    this.logger.warn('This is a destructive action that cannot be undone.');
    this.post('reset', {}, undefined, { folder: folder });
  }

  /**
   * Post with an empty body to immediately restart Syncthing.
   */
  restart(): void {
    this.post('restart');
  }

  /**
   * Resume the given device or all devices.
   *
   *             Takes the optional parameter device (device ID). When omitted, resumes all devices.
   *             Returns status 200 and no content upon success, or status 500 and a plain text error
   *             on failure.
   *
   *             Args:
   *                 device (str): Device ID.
   *
   *             Returns:
   *                 dict: with keys ``success`` and ``error``.
   * @param device
   */
  async resume(device?: string): Promise<{ success: boolean, error: string | null }> {
    try {
      const params = device ? { device: device } : undefined;
      await this.post('resume', undefined, undefined, params);
      return { success: true, error: null };
      /* eslint-disable @typescript-eslint/no-explicit-any */
    } catch (error: any) {
      return { success: false, error: error.message || 'Unknown error' };
    }
  }

  /**
   * Post with an empty body to cause Syncthing to exit and not restart.
   */
  shutdown(): void {
    this.post('shutdown');
  }

  /**
   * Returns information about current system status and resource usage. The CPU percent
   *             value has been deprecated from the API and will always report 0.
   */
  async status(): Promise<{ startTime: string | Date | null }> {
    const response = await this.get<{ startTime: string }>('status');
    keysToDatetime<{ startTime: string }>(response, 'startTime');
    return response;
  }

  /**
   * Checks for a possible upgrade and returns an object describing the newest version
   *             and upgrade possibility.
   */
  upgrade(): Promise<{ latest: string, majorNewer: boolean, newer: boolean, running: string }> {
    return this.get('upgrade');
  }

  /**
   * Returns when there's a newer version than the instance running.
   */
  async canUpgrade(): Promise<boolean> {
    const response = await this.get<{ newer: boolean }>('upgrade');
    return (response && response.newer);
  }

  /**
   * Perform an upgrade to the newest released version and restart. Does nothing if there
   *             is no newer version than currently running.
   */
  doUpgrade(): void {
    this.post('upgrade');
  }

  /**
   * Returns the current Syncthing version information.
   */
  version(): Promise<{ arch: string, longVersion: string, os: string, version: string }> {
    return this.get('version');
  }
}
