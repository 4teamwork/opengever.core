from opengever.base.handlebars import prepare_handlebars_template
from path import Path
from Products.Five.browser import BrowserView
from opengever.base.interfaces import IGeverSettings
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()


class ConfigView(BrowserView):
    """Provides a read only view of the current site configurables.

    Implemented client-sided over JS and the API endpoint.
    """

    def render_form_template(self):
        return prepare_handlebars_template(TEMPLATES_DIR.joinpath('config.html'))


@implementer(IPublishTraverse)
class GetSettingView(BrowserView):
    """View to get values of configuration settings.
    To allow us to traverse to a particular setting,
    we overwrite __getitem__, which is called by traversals
    (for example unrestrictedTraverse), and publishTraverse, which is
    used for traversing to a published item (e.g. url entered in a browser)
    """

    def __call__(self):
        if hasattr(self, "key"):
            return self.__getitem__(self.key)

    def __getitem__(self, key):
        """We overwrite __getitem__ as it is called by the traversal
        method, allowing us to traverse to settings.
        """
        configuration = IGeverSettings(self.context)
        if key in configuration.get_features():
            return configuration.get_features().get(key)
        elif key in configuration.get_settings():
            return configuration.get_settings().get(key)
        raise(KeyError("{} not in gever settings".format(key)))

    def publishTraverse(self, request, name):  # noqa
        """name is the key  of the setting we want to retrieve
        """
        self.key = name
        return self
