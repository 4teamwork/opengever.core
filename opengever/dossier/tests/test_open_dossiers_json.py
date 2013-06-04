from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles, TEST_USER_ID
import json
import transaction


class TestOpenDossiersJson(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestOpenDossiersJson, self).setUp()
        self.grant('Contributor')

    def test_renders_json_containing_all_open_dossiers(self):
        self.store_dossiers(2)
        transaction.commit()

        self.browser.open("http://nohost/plone/list-open-dossiers-json")
        self.assertEquals("application/json", self.browser.headers['Content-Type'])

        json_data = json.loads(self.browser.contents)

        self.assertEquals(json_data,
            [{
                u'url': u'http://nohost/plone/testdossier-1',
                u'path': u'testdossier-1',
                u'review_state': u'dossier-state-active',
                u'title': u'Testdossier 1',
                u'reference_number': u'OG / 1'
            },
            {
                u'url': u'http://nohost/plone/testdossier-2',
                u'path': u'testdossier-2',
                u'review_state': u'dossier-state-active',
                u'title': u'Testdossier 2',
                u'reference_number': u'OG / 2'
            }])

    def test_does_not_include_resolved_dossiers(self):
        self.store_dossiers(1)
        self.resolve_dossier(self.portal.get('testdossier-1'))
        transaction.commit()

        self.browser.open("http://nohost/plone/list-open-dossiers-json")

        json_data = json.loads(self.browser.contents)
        self.assertEquals([], json_data,
                          "the JSON should not contain resolved dossiers")

    def store_dossiers(self, number, title="Testdossier"):
        for i in range(1, number + 1):
            handle = '%s-%s' % (title.lower(), i)
            self.portal.invokeFactory(
                'opengever.dossier.businesscasedossier',
                handle,
                title='%s %s' % (title, i))

            obj = self.portal.get(handle)
            obj.reindexObject(idxs=['modified'])

    def resolve_dossier(self, dossier):
        setRoles(self.portal, TEST_USER_ID, ['Reviewer', 'Manager'])
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(dossier, 'dossier-transition-resolve')
