import { BaseAPI } from './BaseAPI';

export class Config extends BaseAPI {
    /**
     * HTTP REST endpoint for Config calls.
     * Implements endpoints of https://docs.syncthing.net/dev/rest.html#config-endpoints
     */
    protected prefix = '/rest/config/';

    /**
     * Returns the entire config and PUT replaces it.
     */
    config(): Promise<{}> {
        return this.get('');
    }

    /**
     * Returns whether a restart of Syncthing is required for the current config to take effect.
     */
    restartRequired(): Promise<{}> {
        return this.get('restart-required');
    }

    /**
     * Returns all folders as an array. PUT takes an array and POSTs a single object. In both cases
     * if a given folder/device already exists, it’s replaced, otherwise a new one is added.
     */
    folders(): Promise<any> {
        return this.get('folders');
    }

    /**
     * POST a single object. If a given folder already exists, it’s replaced, otherwise a new one is added.
     * @param folder string: Folder ID.
     */
    addFolder(folder: string): void {
        this.post('folders', { folder: folder })
    }

    /**
     * PUT a single object. If the given folders already exist, they are replaced, otherwise new ones are added.
     * @param folder
     */
    addFolders(folder: string[]): void {
        this.put('folders', { folder: folder })
    }

    /**
     * Returns all devices as an array. PUT takes an array and POSTs a single object. In both cases
     * if a given folder/device already exists, it’s replaced, otherwise a new one is added.
     */
    devices(): Promise<string[]> {
        return this.get('devices')
    }

    /**
     * returns the folder/device for the given ID
     * @param folder string: Folder ID.
     */
    folder(folder: string): Promise<{}> {
        return this.get(`folders/${folder}`)
    }
}
