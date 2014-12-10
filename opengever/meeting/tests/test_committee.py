from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase


class TestCommittee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestCommittee, self).setUp()
        self.container = create(Builder('committee_container'))

    def test_committee_can_be_added(self):
        committee = create(Builder('committee').within(self.container))
        self.assertEqual('committee-1', committee.getId())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        browser.login()
        browser.open(self.container, view='++add++opengever.meeting.committee')

        browser.fill({'Title': u'A c\xf6mmittee'}).submit()
        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)

        committee = browser.context
        self.assertEqual('committee-1', committee.getId())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)
        self.assertEqual(u'A c\xf6mmittee', model.title)

    @browsing
    def test_committee_can_be_edited_in_browser(self, browser):
        committee = create(Builder('committee')
                           .within(self.container)
                           .titled(u'My Committee'))

        browser.login().visit(committee, view='edit')
        form = browser.css('#content-core form').first
        self.assertEqual(u'My Committee', form.find_field('Title').value)

        browser.fill({'Title': u'A c\xf6mmittee'}).submit()
        self.assertIn('Changes saved',
                      browser.css('.portalMessage.info dd').text)

        committee = browser.context
        self.assertEqual('committee-1', committee.getId())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(u'A c\xf6mmittee', model.title)
