from App.config import DefaultConfiguration
import App.config
import os


class PathFinder(object):
    """Helper class to provide various Zope2 Instance related paths that are
    otherwise cumbersome to access.
    """

    def __init__(self):
        self._assert_proper_configuration()
        self._instance_home = os.environ['INSTANCE_HOME']
        self._client_home = os.environ['CLIENT_HOME']

    def _assert_proper_configuration(self):
        cfg = App.config._config
        if cfg is None or isinstance(cfg, DefaultConfiguration):
            raise RuntimeError(
                "Zope is not configured properly yet, refusing "
                "operate on paths that might be wrong!")

    @property
    def var(self):
        """Path to {buildout}/var
        """
        return os.path.normpath(os.path.join(self._client_home, '..'))

    @property
    def var_log(self):
        """Path to {buildout}/var/log
        """
        return os.path.join(self.var, 'log')

    @property
    def buildout(self):
        """Path to {buildout}
        """
        return os.path.normpath(os.path.join(self.var, '..'))
