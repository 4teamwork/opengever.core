from collections import OrderedDict
from opengever.base.utils import escape_html
from opengever.ogds.base.utils import get_current_org_unit
from opengever.webactions.interfaces import IWebActionsProvider
from opengever.webactions.interfaces import IWebActionsRenderer
from urllib import urlencode
from urlparse import parse_qs
from urlparse import urlparse
from urlparse import urlunparse
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest


class WebActionsSafeDataGetter(object):

    _attributes_not_to_escape = ["mode", "action_id", "icon_name", "icon_data", "target_url"]

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

    def _pre_formatting(self, webactions_dict):
        return dict((display, map(self._prepare_webaction_data, webactions))
                    for display, webactions in webactions_dict.items())

    def _prepare_webaction_data(self, action):
        data = {key: value if key in self._attributes_not_to_escape else escape_html(value)
                for key, value in action.items()}
        data['target_url'] = self._sanitize_target_url(
            self._interpolate_target_url(data['target_url'])
        )
        return data

    def _sanitize_target_url(self, target_url):
        # Split the url in its components, so we can handle the HTML
        # escape individually (base url vs. query params).
        parsed_target_url = urlparse(target_url)

        # Sanitize the querystring parameters (names and values) because
        # they may contain evil stuff (user input).
        parsed_query = parse_qs(parsed_target_url.query)
        sanitized_query = OrderedDict({
            escape_html(key): [escape_html(item) for item in value]
            for key, value in parsed_query.items()
        })

        # Enhance the query with the default query params. They don't need
        # to be sanitize because they are not user input.
        sanitized_query.update(self._get_default_webaction_parameters())

        # Sanitize the target url. We need to remove the query params so
        # we don't convert the separating ampersand to a HTML entity.
        target_url_without_query = escape_html(
            urlunparse(parsed_target_url._replace(query=""))
        )

        # Put back the sanitized query params into the target url.
        target_url = urlparse(target_url_without_query)
        target_url = target_url._replace(
            query=urlencode(sanitized_query, doseq=True)
        )
        target_url = urlunparse(target_url)

        return target_url

    def _interpolate_target_url(self, target_url):
        # Replace the placeholders with the actual values.
        return target_url.format(
            intid=getUtility(IIntIds).getId(self.context),
            path='/'.join(self.context.getPhysicalPath()),
            uid=self.context.UID(),
        )

    def _get_default_webaction_parameters(self):
        return OrderedDict({
            'context': self.context.absolute_url(),
            'orgunit': get_current_org_unit().id(),
        })


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


class WebActionsActionButtonsRenderer(WebActionsTitleButtonsRenderer):

    display = 'action-buttons'

    label = u'<span class="subMenuTitle actionText">{title}</span>'
