from opengever.base.interfaces import IRedirector
from opengever.base.redirector import RedirectorViewlet
from opengever.testing import FunctionalTestCase

class TestRedirector(FunctionalTestCase):

    def setUp(self):
        super(TestRedirector, self).setUp()
        self.prepareSession()

        self.redirector = IRedirector(self.request)

    def test_stores_and_retrieves_redirects(self):
        self.redirector.redirect('http://www.google.ch', target='named-window')
        self.assertEquals([{'url': 'http://www.google.ch',
                            'target': 'named-window',
                            'timeout': 0}],
                          self.redirector.get_redirects())

    def test_retrieving_a_redirect_removes_it(self):
        self.redirector.redirect('http://www.ebay.ch', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects()))
        self.assertEquals(0, len(self.redirector.get_redirects()))

    def test_pass_remove_false_to_keeps_redirects(self):
        self.redirector.redirect('http://www.yahoo.com', target='named-window')

        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))
        self.assertEquals(1, len(self.redirector.get_redirects(remove=False)))

class TestRedirectorViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestRedirectorViewlet, self).setUp()
        self.prepareSession()

    def test_viewlet_only_redirects_once(self):
        redirector = IRedirector(self.request)
        redirector.redirect('http://www.google.ch', target='named-window')

        viewlet = RedirectorViewlet(self.portal, self.request, {}, {})
        self.assertIn("http://www.google.ch", viewlet.render().strip())

        self.assertEquals("", viewlet.render())
