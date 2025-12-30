import requests

from .base_api import BaseAPI


class Cluster(BaseAPI):
    """ HTTP REST endpoint for Cluster Services.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#cluster-endpoints
    """
    prefix = '/rest/cluster/pending/'

    def delete_pending_device(self, device: str) -> dict:
        """ Remove records from a pending remote device which tried to connect. Valid values for
            the device parameter are those from the corresponding

            Args:
                device (str): Device ID.
        """
        response = self.delete('devices', params={'device': device}, return_response=True)
        error = response.text or None
        return {'success': response.status_code == requests.codes.ok, 'error': error}

    def pending_device(self) -> dict:
        """ Lists remote devices which have tried to connect but are not yet configured in our
            instance.
        """
        return self.get('devices')

    def delete_pending_folders(self, folder: str, device: str) -> dict:
        """ Remove records about a pending folder announced from a remote device. Valid values for
            the folder and device parameters are those from the corresponding GET
            /rest/cluster/pending/folders endpoint. The device parameter is optional and affects
            announcements of this folder from the given device or from any device if omitted.

            Args:
                folder (str): Folder path.
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        response = self.delete('devices', params={'folder': folder, 'device': device}, return_response=True)
        error = response.text or None
        return {'success': response.status_code == requests.codes.ok, 'error': error}

    def pending_folders(self) -> dict:
        """ Lists folders which remote devices have offered to us, but are not yet shared from our
            instance to them. Takes the optional device parameter to only return folders offered by
            a specific remote device. Other offering devices are also omitted from the result.
        """
        return self.delete('folders')
