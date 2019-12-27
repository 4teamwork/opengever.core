import os


class WorkspaceConfig(object):

    @property
    def secret(self):
        return self._get_env('WORKSPACE_SECRET')

    @property
    def configured_well(self):
        """Is True when the configuration is ok.
        """
        return not self.errors

    @property
    def errors(self):
        errors = []

        if not self.secret:
            errors.append('WORKSPACE_SECRET is required')

        return errors

    def _get_env(self, name, default=''):
        value = os.environ.get(name.upper(), default)
        return self._ensure_encoded(value)

    def _ensure_encoded(self, text):
        if isinstance(text, str):
            return text
        elif isinstance(text, unicode):
            return text.encode('utf-8')
        else:
            raise TypeError(type(text))


workspace_config = WorkspaceConfig()
del WorkspaceConfig  # workspace_config should be used.
