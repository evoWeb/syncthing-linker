import { BaseAPI } from './BaseAPI';

export class ClusterAPI extends BaseAPI {
    /**
     * HTTP REST endpoint for Cluster Services.
     * Implements endpoints of https://docs.syncthing.net/dev/rest.html#cluster-endpoints
     */
    protected prefix = '/rest/cluster/pending/';

    /**
     * Remove records from a pending remote device which tried to connect.
     * Valid values for the device parameter are those from the corresponding
     *
     * @param device string: Device ID.
     */
    async deletePendingDevice(device: string): Promise<{ success: boolean; error: string }> {
        const response = await this.delete<{ text: string }>('devices', { device: device });
        return { success: !!response.text, error: response.text };
    }

    /**
     * Lists remote devices which have tried to connect but are not yet configured in our instance.
     *
     * @returns array
     */
    async pendingDevices(): Promise<{}> {
        return this.get('devices');
    }

    /**
     * Remove records about a pending folder announced from a remote device. Valid values for
     *             the folder and device parameters are those from the corresponding GET
     *             /rest/cluster/pending/folders endpoint. The device parameter is optional and affects
     *             announcements of this folder from the given device or from any device if omitted.
     *
     *             Returns:
     *                 dict: with keys ``success`` and ``error``.
     * @param folder string: Folder path.
     * @param device string: Device ID.
     */
    async deletePendingFolders(folder: string, device?: string): Promise<{ success: boolean; error?: string }> {
        const response = await this.delete<{ text: string }>(
            'folders',
            undefined,
            undefined,
            { folder: folder, device: device }
        );
        return { success: !!response.text, error: response.text };
    }

    /**
     * Lists folders which remote devices have offered to us, but are not yet shared from our
     * instance to them. Takes the optional device parameter to only return folders offered by
     * a specific remote device. Other offering devices are also omitted from the result.
     *
     * @returns array
     */
    async pendingFolders(): Promise<{}> {
        return this.get('folders');
    }
}
