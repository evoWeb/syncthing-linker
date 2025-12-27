from .BaseAPI import BaseAPI

class Noauth(BaseAPI):
    """ HTTP REST endpoint for Noauth Services.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#noauth-endpoints
    """

    prefix = '/rest/noauth/'

    def health(self) -> bool:
        """ Returns true if the server replies with a {"status": "OK"} object.

            Returns:
                bool
        """
        return self.get('health').get('status', '') == 'OK'
