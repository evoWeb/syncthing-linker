import { BaseAPI } from './BaseAPI';

export class Debug extends BaseAPI {
    /**
     * HTTP REST endpoint for Debug calls.
     * Implements endpoints of https://docs.syncthing.net/dev/rest.html#debug-endpoints
     */
    protected prefix = '/rest/debug/';

    /**
     * @deprecated Use Profiling endpoints instead
     *
     * Used to capture a profile of what Syncthing is doing on the CPU. See Profiling.
     *
     *             >>> c = ServiceConfig(...)
     *             >>> d = Debug(c)
     *             >>> d
     *             ... #doctest: +ELLIPSIS
     *             {...}
     *             >>> len(d.keys())
     *             2
     *             >>> 'enabled' in d and 'facilities' in d
     *             True
     *             >>> isinstance(d.get('enabled'), list) or d.get('enabled') is None
     *             True
     *             >>> isinstance(d.get('facilities'), dict)
     *             True
     */
    cpuprof(): Promise<any> {
        this.logger.warn('Debug.cpuprof() is deprecated: Use Profiling endpoints instead');
        return this.get('cpuprof');
    }

    /**
     * @deprecated Use Profiling endpoints instead
     *
     * Used to capture a profile of what Syncthing is doing with the heap memory. See Profiling.
     *
     *             >>> c = ServiceConfig(...)
     *             >>> d = Debug(c)
     *             >>> d
     *             ... #doctest: +ELLIPSIS
     *             {...}
     *             >>> len(d.keys())
     *             2
     *             >>> 'enabled' in d and 'facilities' in d
     *             True
     *             >>> isinstance(d.get('enabled'), list) or d.get('enabled') is None
     *             True
     *             >>> isinstance(d.get('facilities'), dict)
     *             True
     */
    heapprof(): Promise<{}> {
        this.logger.warn('Debug.heapprof() is deprecated: Use Profiling endpoints instead');
        return this.get('heapprof');
    }

    /**
     * Collects information about the running instance for troubleshooting purposes. Returns
     *             a “support bundle” as a zipped archive, which should be sent to the developers after
     *             verifying it contains no sensitive personal information. Credentials for the web GUI
     *             and the API key are automatically redacted already.
     */
    support(): Promise<{}> {
        return this.get('support');
    }

    /**
     * Shows diagnostics about a certain file in a shared folder. Takes the folder (folder ID)
     *             and file (folder relative path) parameters.
     *
     *             Args:
     *                 folder (str): Folder ID.
     *                 file (str): file relative path
     * @param folder
     * @param file
     */
    file(folder: string, file: string): Promise<{}> {
        return this.post('file', {}, { folder: folder, file: file });
    }
}
