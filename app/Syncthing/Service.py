from .BaseAPI import BaseAPI

class Service(BaseAPI):
    """ HTTP REST endpoint for Misc Services.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#misc-services-endpoints
    """

    prefix = '/rest/svc/'

    def device_id(self, id_) -> str:
        """ Verifies and formats a device ID. Accepts all currently valid
            formats (52 or 56 characters with or without separators, upper or lower
            case, with trivial substitutions). Takes one parameter, id, and returns
            either a valid device ID in modern format or an error.

            Args:
                id_ (str)

            Raises:
                SyncthingError: when ``id_`` is an invalid length.

            Returns:
                str
        """
        return self.get('deviceid', params={'id': id_}).get('id')

    def language(self) -> dict:
        """ Returns a list of canonicalized localization codes, as picked up
            from the Accept-Language header sent by the browser. By default, this
            API will return a single element that's empty; however, calling:
            func:`Misc.get` directly with `lang` you can set specific headers to
            get values back as intended.

            Returns:
                List[str]

                >>> s = syncthing_factory()
                >>> len(s.misc.language())
                1
                >>> s.misc.language()[0]
                ''
                >>> s.misc.get('lang', headers={'Accept-Language': 'en-us'})
                ['en-us']
        """
        return self.get('lang')

    def random_string(self, length=32) -> str | None:
        """ Returns a strong random generated string (alphanumeric) of the
            specified length.

            Args:
                length (int): default ``32``.

            Returns:
                str

            >>> s = syncthing_factory()
            >>> len(s.misc.random_string())
            32
            >>> len(s.misc.random_string(32))
            32
            >>> len(s.misc.random_string(1))
            1
            >>> len(s.misc.random_string(0))
            32
            >>> len(s.misc.random_string(None))
            32
            >>> import string
            >>> all_letters = string.ascii_letters + string.digits
            >>> all([c in all_letters for c in s.misc.random_string(128)])
            True
            >>> all([c in all_letters for c in s.misc.random_string(1024)])
            True
        """
        return self.get('random/string', params={'length': length}).get('random', None)

    def report(self) -> dict:
        """ Returns the data sent in the anonymous usage report.

            Returns:
                dict

            >>> s = syncthing_factory()
            >>> report = s.misc.report()
            >>> 'version' in report
            True
            >>> 'longVersion' in report
            True
            >>> 'syncthing v' in report['longVersion']
            True
        """
        return self.get('report')
