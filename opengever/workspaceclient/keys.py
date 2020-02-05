from opengever.workspaceclient import logger
from opengever.workspaceclient.exceptions import ServiceKeyMissing
from path import Path
import json
import os


class KeyRegistry(object):
    """The KeyRegistry handles service-keys provided by ftw.tokenauth.
    It returns the right key for a specific url.

    It looks up keys provided by a static directory on the filesystem.
    """
    key_directory = os.path.expanduser(
        os.path.join('~', '.opengever/ftw_tokenauth_keys'))

    def __init__(self):
        self.load_file_system_keys()

    def get_key_for(self, url):
        """Returns the service key matching the given URL.

        Will raise an error if no key is found.
        """
        url = url.strip('/')
        key = self.keys_by_token_uri.get(url)
        if not key:
            raise ServiceKeyMissing(url, self.keys_by_token_uri.keys(),
                                    self.key_directory)

        return key

    @property
    def keys_by_token_uri(self):
        """Returns all registered keys in a dict with the service-app url as
        the key and the full service-key as the value.
        """
        keys = {}
        for key in self.keys:
            service_app_url = key.get('token_uri').replace(
                "@@oauth2-token", "").strip('/')
            keys[service_app_url] = key

        return keys

    def load_file_system_keys(self):
        """Loads the keys stored on the file system.
        """
        self.keys = []
        for key_file in Path(self.key_directory).glob("*.json"):
            key = json.loads(key_file.bytes())
            if "token_uri" not in key:
                logger.warning(
                    'Found a broken workspace service key at {}'.format(
                        str(key_file)))
                continue

            self.add_key(key)

    def add_key(self, key):
        """Adds a key to the available keys.
        """
        self.keys.append(key)


key_registry = KeyRegistry()
