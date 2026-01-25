import RequestBase from './RequestBase';

interface FolderData {
  modTime: string;
  name: string;
  size: number;
  type: string;
  children?: FolderData[];
}

interface Change {
  flags: string;
  sequence: number;
  modified: string;
  name: string;
  size: number;
  version: string[];
}

interface LocalChanges {
  files?: Change[];
  progress?: Change[];
  queued?: Change[];
  rest?: Change[];
  page: number;
  perPage: number;
}

interface FolderStatus {
  globalBytes: number;
  globalDeleted: number;
  globalDirectories: number;
  globalFiles: number;
  globalSymlinks: number;
  globalTotalItems: number;
  ignorePatterns: boolean;
  inSyncBytes: number;
  inSyncFiles: number;
  invalid: string;
  localBytes: number;
  localDeleted: number;
  localDirectories: number;
  localFiles: number;
  localSymlinks: number;
  localTotalItems: number;
  needBytes: number;
  needDeletes: number;
  needDirectories: number;
  needFiles: number;
  needSymlinks: number;
  needTotalItems: number;
  pullErrors: number;
  receiveOnlyChangedBytes: number;
  receiveOnlyChangedDeletes: number;
  receiveOnlyChangedDirectories: number;
  receiveOnlyChangedFiles: number;
  receiveOnlyChangedSymlinks: number;
  receiveOnlyTotalItems: number;
  sequence: number;
  state: string;
  stateChanged: string;
  version: number;
}

export default class Database extends RequestBase {
  /**
   * HTTP REST endpoint for Database calls.
   * Implements endpoints of https://docs.syncthing.net/dev/rest.html#database-endpoints
   */
  protected prefix = '/rest/db/';

  /**
   * Returns the directory tree of the global model. Directories are always JSON objects
   *             (map/dictionary), and files are always arrays of modification time and size. The first
   *             integer is the files modification time, and the second integer is the file size.
   *
   *             The call takes one mandatory folder parameter and two optional parameters. Optional
   *             parameter levels define how deep within the tree we want to dwell down (0-based,
   *             defaults to unlimited depth) Optional parameter prefix defines a prefix within the
   *             tree where to start building the structure.
   *
   *             Args:
   *                 folder (str): The root folder to traverse.
   *                 levels (int): How deep within the tree we want to dwell down.
   *                     (0-based, defaults to unlimited depth)
   *                 prefix (str): Defines a prefix within the tree where to start
   *                     building the structure.
   */
  browse(folder: string, levels?: number, prefix?: string): Promise<[FolderData]> {
    if (levels !== undefined) {
      throw new Error('Assertion failed: levels is not a number or undefined');
    }
    if (prefix !== undefined) {
      throw new Error('Assertion failed: prefix is not a string or undefined');
    }
    return this.get('browse', undefined, undefined, { folder: folder, levels: levels, prefix: prefix });
  }

  /**
   * Returns the completion percentage (0 to 100) and byte / item counts. Takes optional
   *             device and folder parameters:
   *
   *             - folder specifies the folder ID to calculate completion for. An empty or absent folder
   *               parameter means all folders as an aggregate.
   *
   *             - device specifies the device ID to calculate completion for. An empty or absent device
   *               parameter means the local device.
   *
   *             If a device is specified but no folder, completion is calculated for all folders shared
   *             with that device.
   *
   *             Args:
   *                 device (str): The Syncthing device the folder is syncing to.
   *                 folder (str): The folder that is being synced.
   */
  async completion(device: string, folder: string): Promise<number> {
    const response = await this.get<{ completion: number }>(
      'completion',
      undefined,
      undefined,
      {
        folder: folder,
        device: device,
      }
    );
    return response.completion || 0;
  }

  /**
   * Returns most data about a given file, including version and availability.
   * @param folder
   * @param file
   */
  file(folder: string, file: string): Promise<{ local: { name: string, blocksHash: string | null } }> {
    return this.get('file', undefined, undefined, { folder: folder, file: file });
  }

  /**
   * Takes one parameter, folder, and returns the content of the .stignore as the ignored
   *             field. A second field, expanded, provides a list of strings which represent globbing
   *             patterns described by gobwas/glob (based on standard wildcards) that match the patterns
   *             in .stignore and all the includes.
   *
   *             If appropriate, these globs are prepended by the following modifiers:
   *             ``!`` to negate the glob, ``(?i)`` to do case-insensitive matching and
   *             ``(?d)`` to enable removing of ignored files in an otherwise empty
   *             directory.
   * @param folder
   */
  ignores(folder: string): Promise<{ ignore: string[], expanded: string[] }> {
    return this.get('ignores', undefined, undefined, { folder: folder });
  }

  /**
   * Expects a format similar to the output of GET /rest/db/ignores call, but only
   *             containing the ignored field (expanded field should be omitted). It takes one
   *             parameter, folder, and either updates the content of the .stignore echoing it
   *             back as a response, or returns an error.
   * @param folder
   * @param patterns
   */
  setIgnores(folder: string, patterns?: string[]): Promise<{ ignore: string[] }> {
    if (patterns === undefined) {
      patterns = [];
    }
    return this.post('ignores', { ignore: patterns }, undefined, { folder: folder });
  }

  /**
   * Takes one mandatory parameter, folder, and returns the list of files which were changed
   *             locally in a receive-only folder. Thus, they differ from the global state and could be
   *             reverted by pulling from remote devices again, see POST /rest/db/revert.
   *
   *             The results can be paginated using the common pagination parameters.
   * @param folder
   */
  localchanged(folder: string): Promise<LocalChanges> {
    return this.get('localchanged', undefined, undefined, { folder: folder });
  }

  /**
   * Takes one mandatory parameter, folder, and returns lists of files which are needed by
   *             this device in order for it to become in sync.
   *
   *             The results can be paginated using the common pagination parameters. Pagination happens
   *             across the union of all necessary files, that is - across all 3 sections of the
   *             response. For example, given the current need state is as follows:
   *
   *             1 progress has 15 items
   *
   *             2 queued has 3 items
   *
   *             3 rests have 12 items
   *
   *             If you issue a query with page=1 and perpage=10, only the progress section in the
   *             response will have 10 items. If you issue a request query with page=2 and perpage=10,
   *             a progress section will have the last 5 items, a queued section will have all 3
   *             items, and a rest section will have the first 2 items. If you issue a query for
   *             page=3 and perpage=10, you will only have the last 10 items of the rest section.
   *
   *             Args:
   *                 folder (str):
   *                 page (int): If defined, applies pagination across the
   *                     collection of results.
   *                 perpage (int): If defined, applies pagination across the
   *                     collection of results.
   * @param folder
   * @param page
   * @param perpage
   */
  need(folder: string, page?: number, perpage?: number): Promise<LocalChanges> {
    if (page !== undefined) {
      throw new Error('Assertion failed: page is not a number or undefined');
    }
    if (perpage !== undefined) {
      throw new Error('Assertion failed: perpage is not a number or undefined');
    }
    return this.get('ignores', undefined, undefined, { folder: folder, page: page, perpage: perpage });
  }

  /**
   * Request override of a send-only folder. Override means to make the local version
   *             latest, overriding changes made on other devices. This API call does nothing if
   *             the folder is not a send-only folder.
   *
   *             Args:
   *                 folder (str): folder ID.
   * @param folder
   */
  override(folder: string): void {
    this.get('override', undefined, undefined, { folder: folder });
  }

  /**
   * Moves the file to the top of the download queue.
   * @param folder
   * @param file
   */
  prio(folder: string, file: string): void {
    this.get('prio', undefined, undefined, { folder: folder, file: file });
  }

  /**
   * Takes the mandatory parameters folder and device and returns the list of files which
   *             are needed by that remote device in order for it to become in sync with the shared folder.
   *
   *             The results can be paginated using the common pagination parameters.
   * @param folder
   * @param device
   */
  remoteneed(folder: string, device: string): Promise<LocalChanges> {
    return this.get('remoteneed', undefined, undefined, { folder: folder, device: device });
  }

  /**
   * Request revert of a receive-only folder. Reverting a folder means to undo all local
   *             changes. This API call does nothing if the folder is not a receive-only folder.
   *
   *             Takes the mandatory parameter folder (folder ID).
   * @param folder
   */
  revert(folder: string): void {
    this.post('revert', undefined, undefined, { folder: folder });
  }

  /**
   * Request immediate scan. Takes the optional parameters folder (folder ID), sub (path
   *             relative to the folder root) and next (time in seconds). If a folder is omitted or
   *              empty, all folders are scanned. If a sub is given, only this path (and children, in
   *              case it’s a directory) is scanned. The next argument delays Syncthing’s automated
   *              rescan interval for a given number of seconds.
   *
   *             Args:
   *                 folder (str): Folder ID.
   *                 sub (str): Path relative to the folder root. If sub is omitted,
   *                     the entire folder is scanned for changes, otherwise only
   *                     the given path children are scanned.
   *                 delay (int): Delays Syncthing's automated rescan interval for
   *                     a given number of seconds. Called ''next'' in Syncthing docs
   * @param folder
   * @param sub
   * @param delay
   */
  async scan(folder: string, sub?: string, delay?: number): Promise<string> {
    if (sub === undefined) {
      sub = '';
    }
    if (delay !== undefined) {
      throw new Error('Assertion failed: delay is not a number or undefined');
    }
    return this.get('scan', undefined, undefined, { folder: folder, sub: sub, next: delay });
  }

  /**
   * Returns information about the current status of a folder.
   *
   *             Note:
   *                 This is an expensive call, increasing CPU and RAM usage on the
   *                 device. Use sparingly.
   *
   *             Args:
   *                 folder (str): Folder ID.
   * @param folder
   */
  status(folder: string): Promise<FolderStatus> {
    return this.get('status', { folder: folder });
  }
}
