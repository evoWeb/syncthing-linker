import BaseAPI

from Syncthing import string_types

class Database(BaseAPI):
    """ HTTP REST endpoint for Database calls."""

    prefix = '/rest/db/'

    def browse(self, folder, levels=None, prefix=None):
        """ Returns the directory tree of the global model.

            Directories are always JSON objects (map/dictionary), and files are
            always arrays of modification time and size. The first integer is
            the files modification time, and the second integer is the file
            size.

            Args:
                folder (str): The root folder to traverse.
                levels (int): How deep within the tree we want to dwell down.
                    (0 based, defaults to unlimited depth)
                prefix (str): Defines a prefix within the tree where to start
                    building the structure.

            Returns:
                dict
        """
        assert isinstance(levels, int) or levels is None
        assert isinstance(prefix, string_types) or prefix is None
        return self.get('browse', params={'folder': folder,
                                          'levels': levels,
                                          'prefix': prefix})

    def completion(self, device, folder):
        """ Returns the completion percentage (0 to 100) for a given device
            and folder.

            Args:
                device (str): The Syncthing device the folder is syncing to.
                folder (str): The folder that is being synced.

            Returs:
                int
        """
        return self.get(
            'completion',
            params={'folder': folder, 'device': device}
        ).get('completion', None)

    def file(self, folder, file_):
        """ Returns most data available about a given file, including version
            and availability.

            Args:
                folder (str):
                file_ (str):

            Returns:
                dict
        """
        return self.get('file', params={'folder': folder,
                                        'file': file_})

    def ignores(self, folder):
        """ Returns the content of the ``.stignore`` as the ignore field. A
        second field, expanded, provides a list of strings which represent
        globbing patterns described by gobwas/glob (based on standard
        wildcards) that match the patterns in ``.stignore`` and all the
        includes.

        If appropriate these globs are prepended by the following modifiers:
        ``!`` to negate the glob, ``(?i)`` to do case insensitive matching and
        ``(?d)`` to enable removing of ignored files in an otherwise empty
        directory.

            Args:
                folder

            Returns:
                dict
        """
        return self.get('ignores', params={'folder': folder})

    def set_ignores(self, folder, *patterns):
        """ Applies ``patterns`` to ``folder``'s ``.stignore`` file.

            Args:
                folder (str):
                patterns (str):

            Returns:
                dict
        """
        if not patterns:
            return {}
        data = {'ignore': list(patterns)}
        return self.post('ignores', params={'folder': folder}, data=data)

    def need(self, folder, page=None, perpage=None):
        """ Returns lists of files which are needed by this device in order
        for it to become in sync.

            Args:
                folder (str):
                page (int): If defined applies pagination accross the
                    collection of results.
                perpage (int): If defined applies pagination across the
                    collection of results.

            Returns:
                dict
        """
        assert isinstance(page, int) or page is None
        assert isinstance(perpage, int) or perpage is None
        return self.get('need', params={'folder': folder,
                                 'page': page,
                                 'perpage': perpage})

    def override(self, folder):
        """ Request override of a send-only folder.

            Args:
                folder (str): folder ID.

            Returns:
                dict
        """
        self.post('override', params={'folder': folder})

    def prio(self, folder, file_):
        """ Moves the file to the top of the download queue.

            Args:
                folder (str):
                file_ (str):

            Returns:
                dict
        """
        self.post('prio', params={'folder': folder,
                                  'file': file_})

    def scan(self, folder, sub=None, next_=None):
        """ Request immediate rescan of a folder, or a specific path within a
        folder.

            Args:
                folder (str): Folder ID.
                sub (str): Path relative to the folder root. If sub is omitted
                    the entire folder is scanned for changes, otherwise only
                    the given path children are scanned.
                next_ (int): Delays Syncthing's automated rescan interval for
                    a given amount of seconds.

            Returns:
                str
        """
        if not sub:
            sub = ''
        assert isinstance(sub, string_types)
        assert isinstance(next_, int) or next_ is None
        return self.post('scan', params={'folder': folder,
                                         'sub': sub,
                                         'next': next_})

    def status(self, folder):
        """ Returns information about the current status of a folder.

            Note:
                This is an expensive call, increasing CPU and RAM usage on the
                device. Use sparingly.

            Args:
                folder (str): Folder ID.

            Returns:
                dict
        """
        return self.get('status', params={'folder': folder})
