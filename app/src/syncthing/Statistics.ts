import { BaseAPI } from './BaseAPI';

interface Progress {
  lastScan: string;
  lastFile: {
    filename: string;
    at: string;
  };
}

type FolderScan = Record<string, Progress>;

export class StatisticsAPI extends BaseAPI {
  /**
   * HTTP REST endpoint for Statistic calls.
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#statistics-endpoints
   */
  protected prefix = '/rest/stats/';

  /**
   * Returns general statistics about devices. Currently, it only contains the time the device
   * was last seen and the last connection duration.
   */
  device(): Promise<Record<string, { lastSeen: string, lastConnectionDurationS: number }>> {
    return this.get('device');
  }

  /**
   * Returns general statistics about folders. Currently, it contains the last scan time and
   * the last synced file.
   */
  folder(): Promise<FolderScan> {
    return this.get('folder');
  }
}
