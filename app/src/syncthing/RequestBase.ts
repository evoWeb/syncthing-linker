import * as fs from 'fs';
import * as https from 'https';

import SyncthingException from './SyncthingException';
import ServiceConfig from './ServiceConfig';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface RequestConfig {
  method: string;
  headers: Headers;
  signal: AbortSignal;
  agent?: https.Agent;
  body?: string;
}

export interface RequestData {
  device?: string;
  folder?: string | string[];
  ignore?: string[];
  id?: string;
  length?: number;
  message?: string;
}

export interface RequestHeaders {
  'X-API-Key'?: string;
  'Accept-Language'?: string;
}

export interface RequestParameters {
  device?: string;
  folder?: string;
  file?: string;
  levels?: number;
  prefix?: string;
  page?: number;
  perpage?: number;
  sub?: string;
  next?: string;
  since?: number;
  limit?: number;
  timeout?: number;
  events?: string;
  address?: string;
  current?: string;
}

export interface Response<T> {
  data: T;
  status: number;
  statusText: string,
  headers: Headers;
}


export default class RequestBase {
  // Placeholder for HTTP REST API URL prefix.
  protected prefix: string = '';

  protected serviceConfig: ServiceConfig;
  protected verify: boolean;
  protected headers: RequestHeaders;
  protected protocol: string;
  protected url: string;
  protected logger: Console;

  constructor(config: ServiceConfig, logger: Console) {
    if (config.sslCertFile && !fs.existsSync(config.sslCertFile)) {
      throw new SyncthingException(`ssl_cert_file does not exist at location, ${config.sslCertFile}`);
    }

    this.serviceConfig = config;
    this.verify = !!(config.sslCertFile || config.isHttps);
    this.headers = {
      'X-API-Key': config.apiKey
    };
    this.protocol = config.isHttps ? 'https' : 'http';
    this.url = `${this.protocol}://${config.host}:${config.port}`;
    this.logger = logger;
  }

  async get<T>(
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<T> {
    return this.request<T>('GET', this.prefix + endpoint, data, headers, params);
  }

  async post<T>(
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<T> {
    return this.request<T>('POST', this.prefix + endpoint, data, headers, params);
  }

  async put<T>(
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<T> {
    return this.request<T>('PUT', this.prefix + endpoint, data, headers, params);
  }

  async delete<T>(
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<T> {
    return await this.request<T>('DELETE', this.prefix + endpoint, data, headers, params);
  }

  private async request<T>(
    method: HttpMethod,
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<T> {
    const response = await this.raw_request<T>(method, endpoint, data, headers, params);
    if (!response) {
      throw new SyncthingException('No response from Syncthing API');
    }

    if (response && response.status >= 400) {
      throw new SyncthingException(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    if (typeof response.data === 'object' && response.data !== null && 'error' in response.data && response.data.error !== null) {
      throw new SyncthingException(`Response contains the error: ${response.data.error}`);
    }

    return response.data;
  }

  private async raw_request<T>(
    method: HttpMethod,
    endpoint: string,
    data?: RequestData,
    headers?: RequestHeaders,
    params?: RequestParameters
  ): Promise<Response<T>> {
    const url = new URL(endpoint, this.url);
    if (params) {
      Object.entries(params).forEach(([key, value]) =>
        url.searchParams.append(key, String(value))
      );
    }

    const controller = new AbortController(),
      timeoutId = setTimeout(() => controller.abort(), this.serviceConfig.timeout * 1000),
      mergedHeaders = new Headers({
        ...this.headers,
        ...headers,
        'Content-Type': 'application/json'
      }),
      fetchConfig: RequestConfig = {
        method: method.toString().toUpperCase(),
        headers: mergedHeaders,
        signal: controller.signal,
      };

    // Body nur bei entsprechenden Methoden hinzufügen
    if (method !== 'GET' && data && Object.keys(data).length > 0) {
      fetchConfig.body = JSON.stringify(data);
    }

    if (this.verify && this.serviceConfig.sslCertFile) {
      fetchConfig.agent = new https.Agent({
        ca: fs.readFileSync(this.serviceConfig.sslCertFile, 'utf8')
      });
    }

    try {
      const response = await fetch(url.toString(), fetchConfig);
      clearTimeout(timeoutId);

      const isJson = response.headers.get('content-type')?.includes('application/json');
      const responseData = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        throw new SyncthingException(`HTTP request error: ${response.status}`);
      }

      return {
        data: responseData as T,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      };
      /* eslint-disable @typescript-eslint/no-explicit-any */
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new SyncthingException('Request timeout', { cause: error });
      }
      throw error;
    }
  }
}
