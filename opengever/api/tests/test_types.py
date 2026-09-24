from ftw.testbrowser import browsing
from opengever.locking.lock import MOVE_LOCK
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable


BLACKLIST = []


class TestPloneRestAPI(IntegrationTestCase):

    def whitelisted_portal_type_ids(self):
        types_tool = api.portal.get_tool('portal_types')
        portal_type_ids = [typeinfo.id for typeinfo in types_tool.listTypeInfo()]
        return set(portal_type_ids) - set(BLACKLIST)

    @browsing
    def test_rest_api(self, browser):
        broken_types = []
        self.login(self.regular_user, browser)
        for portal_type_id in self.whitelisted_portal_type_ids():
            try:
                # Performing the request within a try-except block will ensure
                # that the traceback will be logged and that we can continue
                # testing the remaining types.
                browser.open(
                    '{}/@types/{}'.format(self.portal.absolute_url(), portal_type_id),
                    method='GET', headers={'Accept': 'application/json'})
            except:
                broken_types.append(portal_type_id)

        self.assertEqual(
            [], broken_types,
            "There was an error on requesting these types")

    @browsing
    def test_no_addable_types_if_dossier_has_move_lock(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}/@types'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )
        addable_types = [t['title'] for t in browser.json if t['addable']]
        self.assertEqual(
            addable_types,
            [u'Business Case Dossier', u'Document', u'Mail', u'Task'],
        )

        ILockable(self.dossier).lock(MOVE_LOCK)
        browser.open(
            '{}/@types'.format(self.dossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )
        addable_types = [t['title'] for t in browser.json if t['addable']]
        self.assertEqual(addable_types, [])

    @browsing
    def test_no_addable_types_if_ancestor_has_move_lock(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            '{}/@types'.format(self.subsubdossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )
        addable_types = [t['title'] for t in browser.json if t['addable']]
        self.assertEqual(
            addable_types,
            [u'Document', u'Mail', u'Task'],
        )

        ILockable(self.dossier).lock(MOVE_LOCK)
        browser.open(
            '{}/@types'.format(self.subsubdossier.absolute_url()),
            headers={'Accept': 'application/json'},
        )
        addable_types = [t['title'] for t in browser.json if t['addable']]
        self.assertEqual(addable_types, [])
