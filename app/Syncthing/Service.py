from .BaseAPI import BaseAPI

class Service(BaseAPI):
    """ HTTP REST endpoint for Misc Services.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#misc-services-endpoints
    """

    prefix = '/rest/svc/'

    def deviceid(self, device_id: str) -> str:
        """ Verifies and formats a device ID. Accepts all currently valid formats (52 or 56
            characters with or without separators, upper or lower case, with trivial
            substitutions). Takes one parameter, id, and returns either a valid device ID in
            modern format or an error.

            Raises:
                SyncthingError: when ``device_id`` is an invalid length.
        """
        return self.get('deviceid', params={'id': device_id}).get('id')

    def lang(self, accept_language: str | None = None) -> list[str]:
        """ Returns a list of canonicalized localization codes, as picked up from the
            Accept-Language header sent by the browser.

            >>> s = syncthing_factory()
            >>> len(s.service.lang())
            1
            >>> s.service.lang()[0]
            ''
            >>> s.service.lang('en-us')
            ['en-us']
            >>> s.service.get('lang', headers={'Accept-Language': 'en-us'})
            ['en-us']
        """
        if accept_language:
            result = self.get('lang', headers={'Accept-Language': accept_language})
        else:
            result = self.get('lang')
        return result

    def random_string(self, length: int = 32) -> str:
        """ Returns a strong random generated string (alphanumeric) of the specified length.
            Takes the length parameter.

            Args:
                length (int): default ``32``.

            >>> s = syncthing_factory()
            >>> len(s.service.random_string())
            32
            >>> len(s.service.random_string(32))
            32
            >>> len(s.service.random_string(1))
            1
            >>> len(s.service.random_string(0))
            32
            >>> len(s.service.random_string(None))
            32
            >>> import string
            >>> all_letters = string.ascii_letters + string.digits
            >>> all([c in all_letters for c in s.misc.random_string(128)])
            True
            >>> all([c in all_letters for c in s.misc.random_string(1024)])
            True
        """
        return self.get('random/string', params={'length': length}).get('random', '')

    def report(self) -> dict:
        """ Returns the data sent in the anonymous usage report.

            >>> s = syncthing_factory()
            >>> report = s.service.report()
            >>> 'version' in report
            True
            >>> 'longVersion' in report
            True
            >>> 'syncthing v' in report['longVersion']
            True
        """
        return self.get('report')
