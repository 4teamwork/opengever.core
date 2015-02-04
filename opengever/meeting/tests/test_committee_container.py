from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase


class TestCommitteeContainer(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestCommitteeContainer, self).setUp()
        self.container = create(Builder('committee_container'))

    @browsing
    def test_commitee_listing_displays_linked_committees(self, browser):
        committee = create(Builder('committee')
                           .having(title=u'My Committee')
                           .within(self.container))
        committee_model = committee.load_model()

        browser.login()
        browser.open(self.container, view='tabbedview_view-committees')
        href = browser.find(u'My Committee').node.attrib['href']
        self.assertEqual(committee_model.get_url(), href)
