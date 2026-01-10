import { BaseAPI } from './BaseAPI';

export class FolderAPI extends BaseAPI {
    /**
     * HTTP REST endpoint for Folder Services.
     * Implements endpoints of https://docs.syncthing.net/dev/rest.html#folder-endpoints
     */
    protected prefix = '/rest/folder/';

    /**
     * Takes one mandatory parameter, folder, and returns the list of errors encountered
     *             during scanning or pulling.
     *
     *             The results can be paginated using the common pagination parameters.
     * @param folder
     */
    errors(folder: string): Promise<{}> {
        return this.get('errors', undefined, undefined, { folder: folder });
    }

    /**
     * Deprecated since the version v0.14.53: This endpoint still works as before but is
     *             deprecated. Use GET /rest/folder/errors instead, which returns the same information.
     */
    pullerrors(): Promise<{}> {
        return this.get('errors');
    }

    /**
     * Takes one mandatory parameter, folder, and returns the list of archived files that
     *             could be recovered. How many versions are available depends on the File Versioning
     *             configuration. Each entry specifies when the file version was archived as the
     *             versionTime, the modTime when it was last modified before being archived, and the size
     *             in bytes.
     * @param folder
     */
    async versions(folder: string): Promise<{}> {
        return this.get('versions', undefined, undefined, { folder: folder });
    }

    /**
     * Restore archived versions of a given set of files. Expects an object with attributes
     *             named after the relative file paths, with timestamps as values matching valid
     *             versionTime entries in the corresponding GET /rest/folder/versions response object.
     *
     *             Takes the mandatory parameter folder (folder ID). Returns an object containing any
     *             error messages that occurred during restoration of the file, with the file path as
     *             an attribute name.
     * @param folder
     * @param files
     */
    restoreVersions(folder: string, files: Record<string, string>): void {
        this.post('versions', files, undefined, { folder: folder });
    }
}
