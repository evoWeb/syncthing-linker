import axios, {AxiosRequestConfig, AxiosResponse} from 'axios';
import * as fs from 'fs';
import * as https from 'https';

import { SyncthingException } from './SyncthingException';
import { ServiceConfig } from './ServiceConfig';

export class BaseAPI {
    // Placeholder for HTTP REST API URL prefix.
    protected prefix: string = '';

    protected serviceConfig: ServiceConfig;
    protected verify: boolean;
    protected headers: any;
    protected protocol: string;
    protected url: string;
    protected logger: Console;

    constructor(config: ServiceConfig, logger?: Console) {
        if (config.sslCertFile && !fs.existsSync(config.sslCertFile)) {
            throw new SyncthingException(`ssl_cert_file does not exist at location, ${config.sslCertFile}`)
        }

        this.serviceConfig = config;
        this.verify = !!(config.sslCertFile || config.isHttps);
        this.headers = {
            'X-API-Key': config.apiKey
        }
        this.protocol = config.isHttps ? 'https' : 'http';
        this.url = `${this.protocol}://${config.host}:${config.port}`;
        this.logger = logger || console;
    }

    protected async raw_request<T>(
        method: string,
        endpoint: string,
        data?: any,
        headers?: any,
        params?: any
    ): Promise<AxiosResponse<T>> {
        method = method.toUpperCase();
        endpoint = new URL(endpoint, this.url).toString();

        if (!['GET', 'POST', 'PUT', 'DELETE'].includes(method)) {
            throw new SyncthingException(`unsupported http verb requested, ${method}`)
        }

        if (data === undefined) {
            data = {}
        }

        if (headers === undefined) {
            headers = {}
        }

        if (typeof data !== 'object' || data === null || Array.isArray(data)) {
            throw new Error('Data must be an object');
        }
        if (typeof headers !== 'object' || headers === null || Array.isArray(headers)) {
            throw new Error('Headers must be an object');
        }

        let result: any;
        try {
            headers = Object.assign(headers, this.headers);

            const axiosConfig: AxiosRequestConfig = {
                method: method,
                url: endpoint,
                data: data,
                params: params,
                timeout: this.serviceConfig.timeout * 1000,
                headers: headers,
            };

            if (this.serviceConfig.isHttps && this.serviceConfig.sslCertFile) {
                axiosConfig.httpsAgent = new https.Agent({
                    ca: fs.readFileSync(this.serviceConfig.sslCertFile)
                });
            }
            result = await axios.request<T>(axiosConfig);
        } catch (error: any) {
            if (axios.isAxiosError(error)) {
                throw new SyncthingException('HTTP request error', { cause: error });
            }
        }
        return result;
    }

    protected async request<T>(method: string, endpoint: string, data?: any, headers?: any, params?: any): Promise<T> {
        const response: AxiosResponse<T> | undefined = await this.raw_request(method, endpoint, data, headers, params);
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

    async get<T>(endpoint: string, data?: any, headers?: any, params?: any): Promise<T> {
        return this.request<T>('GET', this.prefix + endpoint, data, headers, params);
    }

    async post<T>(endpoint: string, data?: any, headers?: any, params?: any): Promise<T> {
        return this.request<T>('POST', this.prefix + endpoint, data, headers, params);
    }

    async put<T>(endpoint: string, data?: any, headers?: any, params?: any): Promise<T> {
        return this.request<T>('PUT', this.prefix + endpoint, data, headers, params);
    }

    async delete<T>(endpoint: string, data?: any, headers?: any, params?: any): Promise<T> {
        return await this.request<T>('DELETE', this.prefix + endpoint, data, headers, params);
    }
}
