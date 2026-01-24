// in seconds
export const DEFAULT_TIMEOUT = 100;

export class ServiceConfig {
  constructor(
    public apiKey: string,
    public host: string = 'localhost',
    public port: number = 8384,
    public timeout: number = DEFAULT_TIMEOUT,
    public isHttps: boolean = false,
    public sslCertFile: string | undefined = undefined,
  ) {
  }
}
