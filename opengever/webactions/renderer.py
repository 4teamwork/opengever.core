from opengever.base.utils import escape_html
from opengever.webactions.interfaces import IWebActionsRenderer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from opengever.webactions.interfaces import IWebActionsProvider
from zope.component import queryMultiAdapter


class WebActionsSafeDataGetter(object):

    _attributes_not_to_escape = ["mode", "action_id", "icon_name", "icon_data"]

    def __init__(self, context, request, display):
        self.context = context
        self.request = request
        self.display = display

    def get_webactions_data(self):
        provider = queryMultiAdapter((self.context, self.request),
                                     IWebActionsProvider)
        if provider is None:
            return dict()

        webactions_dict = provider.get_webactions(self.display)
        return self._pre_formatting(webactions_dict)

    def render_webaction(self, action):
        raise NotImplementedError

    def _pre_formatting(self, webactions_dict):
        return dict((display, map(self._prepare_webaction_data, webactions))
                    for display, webactions in webactions_dict.items())

    def _prepare_webaction_data(self, action):
        return {key: value if key in self._attributes_not_to_escape else escape_html(value)
                for key, value in action.items()}


@implementer(IWebActionsRenderer)
@adapter(Interface, IBrowserRequest)
class BaseWebActionsRenderer(object):
    """Base IWebActionsRenderer implementation serving as baseclass
    for renderers specific to a given display location.
    Attributes/methods that have to be overwritten in a subclass:
        - display: the display location of the webactions.
        - render_webaction: method called on each webaction used to format
                             the data as needed for a given display location
    """

    display = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data_getter = WebActionsSafeDataGetter(self.context, self.request,
                                               self.display)
        webactions = data_getter.get_webactions_data().get(self.display, list())
        return map(self.render_webaction, webactions)

    def render_webaction(self, action):
        raise NotImplementedError


class WebActionsTitleButtonsRenderer(BaseWebActionsRenderer):

    display = 'title-buttons'

    markup = u'<a title="{title}" href="{target_url}" class="{klass}">'\
             u'{image}{label}</a>'
    link_css_klass = 'webaction_button'
    label = ''

    def render_webaction(self, action):
        klass = self.link_css_klass
        image = ''

        if action.get("icon_name"):
            klass += u" fa {icon_name}"
        elif action.get("icon_data"):
            image = u'<img src="{icon_data}" />'
        return self.markup.format(klass=klass.format(**action),
                                  image=image.format(**action),
                                  label=self.label.format(**action),
                                  **action)
