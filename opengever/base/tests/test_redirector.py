from opengever.base.interfaces import IRedirector
from opengever.base.redirector import RedirectorViewlet
from opengever.testing import FunctionalTestCase

class TestRedirector(FunctionalTestCase):

    def setUp(self):
        super(TestRedirector, self).setUp()
        self.grant('Contributor')
        self.prepareSession()

    def test_redirector(self):

        # Register a redirect:
        redirector = IRedirector(request)
        redirector.redirect('http://www.google.ch', target='named-window')

        # Getting the redirect:
        self.assertEquals([{'url': 'http://www.google.ch', 'target': 'named-window', 'timeout': 0}],
                          redirector.get_redirects(remove=False))

        self.assertEquals([{'url': 'http://www.google.ch', 'target': 'named-window', 'timeout': 0}],
                          redirector.get_redirects(remove=True))

        self.assertEquals([], redirector.get_redirects())

        # Test the viewlet with another redirect:
        redirector.redirect('http://www.google.ch', target='named-window')

        # The redirection done with javascript:
        viewlet = RedirectorViewlet(self.portal, request, {}, {})
        self.assertIn("http://www.google.ch", viewlet.render().strip())

        # Only redirect once:
        self.assertEquals("", viewlet.render())
