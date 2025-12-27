from .BaseAPI import BaseAPI

class Config(BaseAPI):
    """ HTTP REST endpoint for Config calls.

        Implements endpoints of https://docs.syncthing.net/dev/rest.html#config-endpoints
    """

    prefix = '/rest/config/'

    def config(self) -> dict:
        """ Returns the entire config and PUT replaces it.

            Returns:
                 dict
        """
        return self.get('')

    def restart_required(self) -> dict:
        """ Returns whether a restart of Syncthing is required for the current config to take effect.

            Returns:
                 dict
        """
        return self.get('restart-required')

    def folders(self) -> list[str]:
        """ Returns all folders as an array. PUT takes an array and POST a single object. In both cases
            if a given folder/device already exists, it’s replaced, otherwise a new one is added.

            Returns:
                 List[str]
        """
        return self.get('folders')

    def add_folder(self, folder: str) -> None:
        """ POST a single object. If a given folder already exists, it’s replaced, otherwise a new one is added.

            Returns:
                 List[str]
        """
        self.post('folders', data={'folder': folder})

    def add_folders(self, folder: list[str]) -> None:
        """ PUT a single object. If the given folders already exist, they are replaced, otherwise new ones are added.

            Returns:
                 List[str]
        """
        self.put('folders', data={'folder': folder})

    def devices(self) -> list[str]:
        """ Returns all devices as an array. PUT takes an array and POST a single object. In both cases
            if a given folder/device already exists, it’s replaced, otherwise a new one is added.

            Returns:
                 List[str]
        """
        return self.get('devices')