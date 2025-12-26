from .BaseAPI import BaseAPI

class Statistics(BaseAPI):
    """ HTTP REST endpoint for Statistic calls."""

    prefix = '/rest/stats/'

    def device(self):
        """ Returns general statistics about devices.

            Currently, it only contains the time the device was last seen.

            Returns:
                dict
        """
        return self.get('device')

    def folder(self):
        """ Returns general statistics about folders.

            Currently, it contains the last scan time and the last synced file.

            Returns:
                dict
        """
        return self.get('folder')
