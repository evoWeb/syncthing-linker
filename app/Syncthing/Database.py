from .BaseAPI import BaseAPI

class Database(BaseAPI):
    """ HTTP REST endpoint for Database calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#database-endpoints
    """

    prefix = '/rest/db/'

    def browse(self, folder: str, levels: int = None, prefix: str = None) -> dict:
        """ Returns the directory tree of the global model. Directories are always JSON objects
            (map/dictionary), and files are always arrays of modification time and size. The first
            integer is the files modification time, and the second integer is the file size.

            The call takes one mandatory folder parameter and two optional parameters. Optional
            parameter levels define how deep within the tree we want to dwell down (0-based,
            defaults to unlimited depth) Optional parameter prefix defines a prefix within the
            tree where to start building the structure.

            Args:
                folder (str): The root folder to traverse.
                levels (int): How deep within the tree we want to dwell down.
                    (0-based, defaults to unlimited depth)
                prefix (str): Defines a prefix within the tree where to start
                    building the structure.
        """
        assert isinstance(levels, int) or levels is None
        assert isinstance(prefix, str) or prefix is None
        return self.get('browse', params={'folder': folder, 'levels': levels, 'prefix': prefix})

    def completion(self, device: str, folder: str) -> int:
        """ Returns the completion percentage (0 to 100) and byte / item counts. Takes optional
            device and folder parameters:

            - folder specifies the folder ID to calculate completion for. An empty or absent folder
              parameter means all folders as an aggregate.

            - device specifies the device ID to calculate completion for. An empty or absent device
              parameter means the local device.

            If a device is specified but no folder, completion is calculated for all folders shared
            with that device.

            Args:
                device (str): The Syncthing device the folder is syncing to.
                folder (str): The folder that is being synced.
        """
        return self.get('completion', params={'folder': folder, 'device': device}).get('completion', None)

    def file(self, folder: str, file: str) -> dict:
        """ Returns most data about a given file, including version and availability. """
        return self.get('file', params={'folder': folder, 'file': file})

    def ignores(self, folder: str) -> dict:
        """ Takes one parameter, folder, and returns the content of the .stignore as the ignored
            field. A second field, expanded, provides a list of strings which represent globbing
            patterns described by gobwas/glob (based on standard wildcards) that match the patterns
            in .stignore and all the includes.

            If appropriate, these globs are prepended by the following modifiers:
            ``!`` to negate the glob, ``(?i)`` to do case-insensitive matching and
            ``(?d)`` to enable removing of ignored files in an otherwise empty
            directory.
        """
        return self.get('ignores', params={'folder': folder})

    def set_ignores(self, folder: str, *patterns) -> dict:
        """ Expects a format similar to the output of GET /rest/db/ignores call, but only
            containing the ignored field (expanded field should be omitted). It takes one
            parameter, folder, and either updates the content of the .stignore echoing it
            back as a response, or returns an error.
        """
        if not patterns:
            return {}
        data = {'ignore': list(patterns)}
        return self.post('ignores', params={'folder': folder}, data=data)

    def localchanged(self, folder: str) -> dict:
        """ Takes one mandatory parameter, folder, and returns the list of files which were changed
            locally in a receive-only folder. Thus, they differ from the global state and could be
            reverted by pulling from remote devices again, see POST /rest/db/revert.

            The results can be paginated using the common pagination parameters.
        """
        return self.get('localchanged', params={'folder': folder})

    def need(self, folder: str, page: int = None, perpage: int = None) -> dict:
        """ Takes one mandatory parameter, folder, and returns lists of files which are needed by
            this device in order for it to become in sync.

            The results can be paginated using the common pagination parameters. Pagination happens
            across the union of all necessary files, that is - across all 3 sections of the
            response. For example, given the current need state is as follows:

            1 progress has 15 items

            2 queued has 3 items

            3 rests have 12 items

            If you issue a query with page=1 and perpage=10, only the progress section in the
            response will have 10 items. If you issue a request query with page=2 and perpage=10,
            a progress section will have the last 5 items, a queued section will have all 3
            items, and a rest section will have the first 2 items. If you issue a query for
            page=3 and perpage=10, you will only have the last 10 items of the rest section.

            Args:
                folder (str):
                page (int): If defined, applies pagination across the
                    collection of results.
                perpage (int): If defined, applies pagination across the
                    collection of results.
        """
        assert isinstance(page, int) or page is None
        assert isinstance(perpage, int) or perpage is None
        return self.get('need', params={'folder': folder, 'page': page, 'perpage': perpage})

    def override(self, folder: str) -> None:
        """ Request override of a send-only folder. Override means to make the local version
            latest, overriding changes made on other devices. This API call does nothing if
            the folder is not a send-only folder.

            Args:
                folder (str): folder ID.
        """
        self.post('override', params={'folder': folder})

    def prio(self, folder: str, file: str) -> None:
        """ Moves the file to the top of the download queue. """
        self.post('prio', params={'folder': folder, 'file': file})

    def remoteneed(self, folder: str, device: str) -> dict:
        """ Takes the mandatory parameters folder and device and returns the list of files which
            are needed by that remote device in order for it to become in sync with the shared folder.

            The results can be paginated using the common pagination parameters.
        """
        return self.get('remoteneed', params={'folder': folder, 'device': device})

    def revert(self, folder: str) -> None:
        """ Request revert of a receive-only folder. Reverting a folder means to undo all local
            changes. This API call does nothing if the folder is not a receive-only folder.

            Takes the mandatory parameter folder (folder ID).
        """
        self.post('revert', params={'folder': folder})

    def scan(self, folder: str, sub: str = None, delay: int = None) -> str:
        """ Request immediate scan. Takes the optional parameters folder (folder ID), sub (path
            relative to the folder root) and next (time in seconds). If a folder is omitted or
             empty, all folders are scanned. If a sub is given, only this path (and children, in
             case it’s a directory) is scanned. The next argument delays Syncthing’s automated
             rescan interval for a given number of seconds.

            Args:
                folder (str): Folder ID.
                sub (str): Path relative to the folder root. If sub is omitted,
                    the entire folder is scanned for changes, otherwise only
                    the given path children are scanned.
                delay (int): Delays Syncthing's automated rescan interval for
                    a given number of seconds. Called ''next'' in Syncthing docs
        """
        if not sub:
            sub = ''
        assert isinstance(sub, str)
        assert isinstance(delay, int) or delay is None
        return self.post('scan', params={'folder': folder, 'sub': sub, 'next': delay})

    def status(self, folder: str) -> dict:
        """ Returns information about the current status of a folder.

            Note:
                This is an expensive call, increasing CPU and RAM usage on the
                device. Use sparingly.

            Args:
                folder (str): Folder ID.
        """
        return self.get('status', params={'folder': folder})
