import RequestBase from './RequestBase';

export default class Noauth extends RequestBase {
  /**
   * HTTP REST endpoint for Noauth Services.
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#noauth-endpoints
   */
  protected prefix = '/rest/noauth/';

  /**
   * Returns true if the server replies with a {"status": "OK"} object.
   */
  async health(): Promise<boolean> {
    const data = await this.get<{ status: string }>('health');
    return data.status === 'OK';
  }
}
