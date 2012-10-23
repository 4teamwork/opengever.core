from five import grok
from opengever.base.interfaces import IRedirector
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.app.layout.viewlets.interfaces import IAboveContentTitle

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


REDIRECTOR_SESS_KEY = 'opengever_base_IRedirector'


class Redirector(grok.Adapter):
    """An adapter for the BrowserRequest to redirect a user after loading the
    next page to a specific URL which is opened in another window / tab with
    the name "target".
    """

    grok.provides(IRedirector)
    grok.context(IBrowserRequest)

    def __init__(self, request):
        self.request = request
        try:
            self.session = request.SESSION
        except AttributeError:
            self.session = {}

    def redirect(self, url, target='_blank', timeout=0):
        """Redirects the user to a `url` which is opened in a window called
        `target` after loading the next page.
        """

        if REDIRECTOR_SESS_KEY not in self.session.keys():
            self.session[REDIRECTOR_SESS_KEY] = PersistentList()

        data = PersistentDict()
        data['url'] = url
        data['target'] = target
        data['timeout'] = int(timeout)

        self.session[REDIRECTOR_SESS_KEY].append(data)

    def get_redirects(self, remove=True):
        """Returns a list of dicts containing the redirect informations.
        """

        if REDIRECTOR_SESS_KEY not in self.session.keys():
            return []
        else:
            redirects = self.session[REDIRECTOR_SESS_KEY]
            if remove:
                del self.session[REDIRECTOR_SESS_KEY]
            return redirects


class RedirectorViewlet(grok.Viewlet):
    """ Viewlet which adds the redirects for the IRedirector.
    """

    grok.name('redirector')
    grok.context(Interface)
    grok.viewletmanager(IAboveContentTitle)
    grok.require('zope2.View')

    JS_TEMPLATE = '''
<script type="text/javascript">
$(function() {
    window.setTimeout("window.open('%(url)s', '%(target)s');", %(timeout)s);
});
</script>
'''

    def render(self):
        redirector = IRedirector(self.request)
        redirects = redirector.get_redirects(remove=True)
        html = []
        for redirect in redirects:
            html.append(RedirectorViewlet.JS_TEMPLATE % redirect)

        return ''.join(html)
