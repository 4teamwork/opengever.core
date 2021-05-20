from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.inbox.inbox import IInbox
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from unittest import skip
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


class TestInbox(FunctionalTestCase):

    @browsing
    def test_adding(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open()
        factoriesmenu.add('Inbox')
        browser.fill({'Title (German)': u'Eingangsk\xf6rbli',
                      'Title (English)': u'Inbox'}).save()

        statusmessages.assert_no_error_messages()
        self.assertTrue(IInbox.providedBy(browser.context))

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(browser.context)
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_inbox_policy", config.getPolicyBelowId())

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        browser.login().open()

        self.grant('Administrator')
        browser.reload()
        self.assertNotIn(
            'Inbox',
            factoriesmenu.addable_types()
            )

        self.grant('Manager')
        browser.reload()
        self.assertIn(
            'Inbox',
            factoriesmenu.addable_types()
            )

    def test_get_responsible_org_unit_fetch_configured_org_unit(self):
        inbox = create(Builder('inbox').
                       having(responsible_org_unit='org-unit-1'))

        self.assertEqual(self.org_unit, inbox.get_responsible_org_unit())

    def test_get_responsible_org_unit_returns_none_when_no_org_unit_is_configured(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_responsible_org_unit())

    def test_get_sequence_number_returns_none(self):
        inbox = create(Builder('inbox'))

        self.assertEqual(None, inbox.get_sequence_number())
        transaction.commit()

    @skip("This test currently fails in a flaky way on CI."
          "See https://github.com/4teamwork/opengever.core/issues/3995")
    @browsing
    def test_supports_translated_title(self, browser):
        add_languages(['de-ch', 'fr-ch'])
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Inbox')
        browser.fill({'Title (German)': u'Eingangskorb',
                      'Title (French)': u'Bo\xeete de r\xe9ception'})
        browser.find('Save').click()

        browser.find(u'Fran\xe7ais').click()
        self.assertEquals(u'Bo\xeete de r\xe9ception',
                          browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Eingangskorb',
                          browser.css('h1').first.text)

    @browsing
    def test_portlet_inheritance_is_blocked(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open()
        factoriesmenu.add('Inbox')
        browser.fill({'Title (German)': u'Eingangsk\xf6rbli',
                      'Title (English)': u'Inbox'}).save()

        statusmessages.assert_no_error_messages()
        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', browser.context)

    @browsing
    def test_navigation_portlet_is_added(self, browser):
        inboxcontainer = create(Builder('inbox_container'))

        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(inboxcontainer)
        factoriesmenu.add('Inbox')
        browser.fill({'Title (German)': u'Eingangsk\xf6rbli',
                      'Title (English)': u'Inbox'}).save()

        statusmessages.assert_no_error_messages()

        manager = getUtility(
            IPortletManager, name=u'plone.leftcolumn', context=browser.context)
        mapping = getMultiAdapter(
            (browser.context, manager), IPortletAssignmentMapping)
        portlet = mapping.get('navigation')

        self.assertIsNotNone(portlet, 'Navigation portlet not added to Inbox.')
        self.assertFalse(portlet.currentFolderOnly)
        self.assertEquals(0, portlet.topLevel)
        self.assertEquals('opengever-inbox-container/opengever-inbox-inbox',
                          portlet.root)
