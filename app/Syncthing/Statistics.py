from .BaseAPI import BaseAPI

class Statistics(BaseAPI):
    """ HTTP REST endpoint for Statistic calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#statistics-endpoints
    """

    prefix = '/rest/stats/'

    def device(self) -> dict:
        """ Returns general statistics about devices. Currently, only contains the time the device
            was last seen and the last connection duration.

            Returns:
                dict
        """
        return self.get('device')

    def folder(self) -> dict:
        """ Returns general statistics about folders. Currently, contains the last scan time and
            the last synced file.

            Returns:
                dict
        """
        return self.get('folder')
