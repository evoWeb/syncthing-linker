import { ServiceConfig, DEFAULT_TIMEOUT } from './syncthing/ServiceConfig';

export class AppConfig extends ServiceConfig {
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
}