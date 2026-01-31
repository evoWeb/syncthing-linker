import * as fs from 'fs';

import ServiceConfig, { DEFAULT_TIMEOUT } from './syncthing/ServiceConfig';

export default class AppConfig extends ServiceConfig {
  constructor(
    apiKey: string,
    host: string = 'localhost',
    port: number = 8384,
    timeout: number = DEFAULT_TIMEOUT,
    isHttps: boolean = false,
    sslCertFile: string | undefined = undefined,
    public source: string = '/files/source/',
    public destination: string = '/files/destination/',
    public filters: string[] = [],
    public excludes: RegExp | undefined = undefined,
  ) {
    super(apiKey, host, port, timeout, isHttps, sslCertFile);
  }

  static getInstance(configPath: string = '/config/config.json'): AppConfig {
    const fileContents = fs.readFileSync(configPath, 'utf8'),
      config: any = JSON.parse(fileContents);

    if (!config) {
      throw new Error('Configuration is empty.');
    }

    const apiKey = process.env.SYNCTHING_API_KEY || '';
    if (!apiKey) {
      throw new Error('No API key found.');
    }

    const host: string = process.env.SYNCTHING_HOST || '127.0.0.1',
      port: number = parseInt(process.env.SYNCTHING_PORT || '8384'),
      isHttps: boolean = ['1', 'true', 'yes'].includes((process.env.SYNCTHING_HTTPS || '0').toLowerCase()),
      sslCertFile: string | undefined = process.env.SYNCTHING_CERT_FILE;

    return new AppConfig(
      apiKey,
      host,
      port,
      parseInt(process.env.SYNCTHING_TIMEOUT || '60'),
      isHttps,
      sslCertFile,
      config.source || '/files/source/',
      config.destination || '/files/destination/',
      (config.filter || 'ItemFinished').split(','),
      new RegExp(config.excludes || '')
    );
  }
}
