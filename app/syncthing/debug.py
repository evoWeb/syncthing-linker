from .base_api import BaseAPI


class Debug(BaseAPI):
    """ HTTP REST endpoint for Debug calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#debug-endpoints
    """

    prefix = '/rest/debug/'

    # DEPRECATED
    def cpuprof(self) -> dict:
        """ Used to capture a profile of what Syncthing is doing on the CPU. See Profiling.

            >>> s = Syncthing.create_instance().debug
            >>> debug = s.debug()
            >>> debug
            ... #doctest: +ELLIPSIS
            {...}
            >>> len(debug.keys())
            2
            >>> 'enabled' in debug and 'facilities' in debug
            True
            >>> isinstance(debug.get('enabled'), list) or debug.get('enabled') is None
            True
            >>> isinstance(debug.get('facilities'), dict)
            True
        """
        return self.get('cpuprof')

    # DEPRECATED
    def heapprof(self) -> dict:
        """ Used to capture a profile of what Syncthing is doing with the heap memory. See Profiling.

            >>> s = Syncthing.create_instance().system
            >>> debug = s.debug()
            >>> debug
            ... #doctest: +ELLIPSIS
            {...}
            >>> len(debug.keys())
            2
            >>> 'enabled' in debug and 'facilities' in debug
            True
            >>> isinstance(debug.get('enabled'), list) or debug.get('enabled') is None
            True
            >>> isinstance(debug.get('facilities'), dict)
            True
        """
        return self.get('heapprof')

    def support(self) -> dict:
        """ Collects information about the running instance for troubleshooting purposes. Returns
            a “support bundle” as a zipped archive, which should be sent to the developers after
            verifying it contains no sensitive personal information. Credentials for the web GUI
            and the API key are automatically redacted already.
        """
        return self.get('support')

    def file(self, folder: str, file: str) -> dict:
        """ Shows diagnostics about a certain file in a shared folder. Takes the folder (folder ID)
            and file (folder relative path) parameters.

            Args:
                folder (str): Folder ID.
                file (str): file relative path
        """
        return self.post('file', params={'folder': folder, 'file': file})