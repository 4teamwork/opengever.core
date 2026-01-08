from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase


class TestRoleAssignmentReportGet(SolrIntegrationTestCase):

    @browsing
    def test_role_assignment_report(self, browser):
        self.login(self.administrator, browser=browser)

        url = "{absolute_url}/@role-assignment-report?filters.principal_ids:record:list={regular_user}".format(
            absolute_url=self.portal.absolute_url(),
            regular_user=self.regular_user.getId()
        )
        browser.open(url, method='GET', headers=self.api_headers)
        expected_data = {
            u'@id': u'http://nohost/plone/@role-assignment-report?filters.principal_ids%3Arecord%3Alist=regular_user',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'UID': u'createtreatydossiers000000000001',
                    u'description': u'Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                    u'is_leafnode': None,
                    u'reference': u'Client1 1.1 / 1',
                    u'review_state': u'dossier-state-active',
                    u'role_Contributor': [],
                    u'role_DossierManager': [],
                    u'role_Editor': [],
                    u'role_Publisher': [],
                    u'role_Reader': [],
                    u'role_Reviewer': [],
                    u'role_Role Manager': [],
                    u'role_TaskResponsible': [u'regular_user'],
                    u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5',
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'UID': u'createexpireddossier000000000001',
                    u'description': u'Abgeschlossene Vertr\xe4ge vor 2000.',
                    u'is_leafnode': None,
                    u'reference': u'Client1 1.1 / 2',
                    u'review_state': u'dossier-state-resolved',
                    u'role_Contributor': [],
                    u'role_DossierManager': [],
                    u'role_Editor': [],
                    u'role_Publisher': [],
                    u'role_Reader': [],
                    u'role_Reviewer': [],
                    u'role_Role Manager': [],
                    u'role_TaskResponsible': [u'regular_user'],
                    u'title': u'Abgeschlossene Vertr\xe4ge'
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6',
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'UID': u'createinactivedossier00000000001',
                    u'description': u'Inaktive Vertr\xe4ge von 2016.',
                    u'is_leafnode': None,
                    u'reference': u'Client1 1.1 / 3',
                    u'review_state': u'dossier-state-inactive',
                    u'role_Contributor': [],
                    u'role_DossierManager': [],
                    u'role_Editor': [],
                    u'role_Publisher': [],
                    u'role_Reader': [],
                    u'role_Reviewer': [],
                    u'role_Role Manager': [],
                    u'role_TaskResponsible': [u'regular_user'],
                    u'title': u'Inaktive Vertr\xe4ge'
                },
                                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17',
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'UID': u'createprotecteddossiers000000003',
                    u'description': u'Schl\xe4cht',
                    u'is_leafnode': None,
                    u'reference': u'Client1 1.1 / 11',
                    u'review_state': u'dossier-state-active',
                    u'role_Contributor': [],
                    u'role_DossierManager': [],
                    u'role_Editor': [],
                    u'role_Publisher': [],
                    u'role_Reader': [],
                    u'role_Reviewer': [],
                    u'role_Role Manager': [],
                    u'role_TaskResponsible': [u'regular_user'],
                    u'title': u'Zu allem \xdcbel'
                }
            ],
            u'items_total': 4,
            u'referenced_roles': [
                {u'id': u'Reader', u'title': u'Read'},
                {u'id': u'Contributor', u'title': u'Add dossiers'},
                {u'id': u'Editor', u'title': u'Edit dossiers'},
                {u'id': u'Reviewer', u'title': u'Resolve dossiers'},
                {u'id': u'Publisher', u'title': u'Reactivate dossiers'},
                {u'id': u'DossierManager', u'title': u'Manage dossiers'},
                {u'id': u'TaskResponsible', u'title': u'Task responsible'},
                {u'id': u'Role Manager', u'title': u'Role manager'}
            ]
        }
        self.assertEqual(200, browser.status_code)
        self.assertEqual(expected_data, browser.json)
