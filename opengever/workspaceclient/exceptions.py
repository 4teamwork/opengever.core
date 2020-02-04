class ServiceKeyMissing(Exception):

    def __init__(self, url, keys, path):
        known_key_urls = repr(tuple(keys))

        super(ServiceKeyMissing, self).__init__(
            'No workspace service key found for URL {}.\n'
            'Found keys {} in the folder: {}'.format(url, known_key_urls, path))
