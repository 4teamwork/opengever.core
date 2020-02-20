class ServiceKeyMissing(Exception):

    def __init__(self, url, keys, path):
        known_key_urls = repr(tuple(keys))

        super(ServiceKeyMissing, self).__init__(
            'No workspace service key found for URL {}.\n'
            'Found keys {} in the folder: {}'.format(url, known_key_urls, path))


class WorkspaceURLMissing(Exception):

    def __init__(self):
        super(WorkspaceURLMissing, self).__init__(
            'The WorkspaceClient does not know where to dispatch the request.\n'
            'Please specify a URL to the workspace through the environment '
            'variable: TEAMRAUM_URL ')


class WorkspaceClientFeatureNotEnabled(Exception):

    def __init__(self):
        super(WorkspaceClientFeatureNotEnabled, self).__init__(
            'Please activate the workspace client feature in the portal '
            'registry in the IWorkspaceClientSettings')


class WorkspaceNotLinked(Exception):

    def __init__(self):
        super(WorkspaceNotLinked, self).__init__(
            'The workspace in not linked with the current dossier.')


class WorkspaceNotFound(Exception):

    def __init__(self):
        super(WorkspaceNotFound, self).__init__(
            'No workspace found.')
