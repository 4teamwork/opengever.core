from five import grok
from opengever.base.interfaces import IRedirector
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.app.layout.viewlets.interfaces import IAboveContentTitle
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

REDIRECTOR_SESS_KEY = 'opengever_base_IRedirector'

REMOTE_CLIENT_KEY = 'remote_client'

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
        And expose-view when the remote_client_key is set in the request
    """

    grok.name('redirector')
    grok.context(Interface)
    grok.viewletmanager(IAboveContentTitle)
    grok.require('zope2.View')

    JS_TEMPLATE = '''
<script type="text/javascript">
jq(function() {
    window.setTimeout("window.open('%(url)s', '%(target)s');", %(timeout)s);
});
</script>
'''


    REMOTE_CLIENT_JS = '''
<script type="text/javascript">
jq(function() {
    jq('#portal-column-content').expose({closeOnClick: false, closeOnEsc: false});
    jq('#portal-breadcrumbs').append('<span style="float:right"><a href="javascript:window.close()">Fenster schliessen</a></span')
});
</script>
'''

    def render(self):
        redirector = IRedirector(self.request)
        redirects = redirector.get_redirects(remove=True)
        html = []
        for redirect in redirects:
            html.append(RedirectorViewlet.JS_TEMPLATE % redirect)

        if REMOTE_CLIENT_KEY in self.request.keys(
                ) and self.request[REMOTE_CLIENT_KEY] == '1':
            html.append(RedirectorViewlet.REMOTE_CLIENT_JS)
        return ''.join(html)
