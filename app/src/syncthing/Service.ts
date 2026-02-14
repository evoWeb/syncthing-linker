import RequestBase from './RequestBase';

interface FolderUses {
  ignorePerms: number;
  autoNormalize: number;
  sendonly: number;
  ignoreDelete: number;
}

interface Announce {
  defaultServersIP: number;
  otherServers: number;
  globalEnabled: boolean;
  defaultServersDNS: number;
  localEnabled: boolean;
}

interface Relays {
  defaultServers: number;
  enabled: boolean;
  otherServers: number;
}

interface DeviceUses {
  compressMetadata: number;
  customCertName: number;
  staticAddr: number;
  compressAlways: number;
  compressNever: number;
  introducer: number;
  dynamicAddr: number;
}

interface UsageReport {
  folderMaxMiB: number;
  platform: string;
  totMiB: number;
  longVersion: string;
  upgradeAllowedManual: boolean;
  totFiles: number;
  folderUses: FolderUses;
  memoryUsageMiB: number;
  version: string;
  sha256Perf: number;
  numFolders: number;
  memorySize: number;
  announce: Announce;
  usesRateLimit: boolean;
  numCPU: number;
  uniqueID: string;
  urVersion: number;
  rescanIntvs: number[];
  numDevices: number;
  folderMaxFiles: number;
  relays: Relays;
  deviceUses: DeviceUses;
  upgradeAllowedAuto: boolean;
}

export default class Service extends RequestBase {
  /**
   * HTTP REST endpoint for Misc Services.
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#misc-services-endpoints
   */
  protected prefix = '/rest/svc/';

  /**
   * Verifies and formats a device ID. Accepts all currently valid formats (52 or 56
   *             characters with or without separators, upper or lower case, with trivial
   *             substitutions). Takes one parameter, id, and returns either a valid device ID in
   *             modern format or an error.
   *
   *             Raises:
   *                 SyncthingError: when ``device_id`` is an invalid length.
   * @param id
   */
  async deviceId(id: string): Promise<string> {
    const data = await this.get<{ id: string }>('deviceid', { id: id });
    return data.id;
  }

  /**
   * Returns a list of canonicalized localization codes, as picked up from the
   *             Accept-Language header sent by the browser.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = Service(c)
   *             >>> len(s.lang())
   *             1
   *             >>> s.lang()[0]
   *             ''
   *             >>> s.lang('en-us')
   *             ['en-us']
   *             >>> s.get('lang', headers={'Accept-Language': 'en-us'})
   *             ['en-us']
   * @param acceptLanguage
   */
  lang(acceptLanguage: string | undefined = undefined): Promise<string[]> {
    let headers = undefined;
    if (acceptLanguage) {
      headers = { 'Accept-Language': acceptLanguage };
    }
    return this.get('lang', undefined, headers);
  }

  /**
   * Returns a strong random generated string (alphanumeric) of the specified length.
   *             Takes the length parameter.
   *
   *             Args:
   *                 length (int): default ``32``.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = Service(c)
   *             >>> len(s.random_string())
   *             32
   *             >>> len(s.random_string(32))
   *             32
   *             >>> len(s.random_string(1))
   *             1
   *             >>> len(s.random_string(0))
   *             32
   *             >>> len(s.random_string())
   *             32
   *             >>> import string
   *             >>> all_letters = string.ascii_letters + string.digits
   *             >>> all([c in all_letters for c in s.random_string(128)])
   *             True
   *             >>> all([c in all_letters for c in s.random_string(1024)])
   *             True
   * @param length
   */
  async randomString(length: number = 32): Promise<string> {
    const data = await this.get<{ random: string }>('random/string', { length: length });
    return data.random || '';
  }

  /**
   * Returns the data sent in the anonymous usage report.
   *
   *             >>> c = ServiceConfig(...)
   *             >>> s = Service(c)
   *             >>> report = s.report()
   *             >>> 'version' in report
   *             True
   *             >>> 'longVersion' in report
   *             True
   *             >>> 'syncthing v' in report.get('longVersion')
   *             True
   */
  report(): Promise<UsageReport> {
    return this.get('report');
  }
}
