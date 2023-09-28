from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
import json


class TestGrantRoleManagerToResponsibleFeature(IntegrationTestCase):

    features = (
        'grant_role_manager_to_responsible',
    )

    def get_assignments_via_responsible(self, obj):
        manager = RoleAssignmentManager(obj)
        return manager.get_assignments_by_cause(ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE)

    @browsing
    def test_responsible_is_granted_role_manager_when_dossier_created(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder,
                         view='++add++opengever.dossier.businesscasedossier')
            browser.fill({'Title': 'Dossier B with relations'})
            browser.find('Save').click()

        self.assertEqual(1, len(children["added"]))
        dossier = children["added"].pop()

        assignments = self.get_assignments_via_responsible(dossier)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': ['Role Manager'],
             'reference': Oguid.for_object(dossier).id,
             'principal': 'kathi.barfuss'},
            assignments[0])

    @browsing
    def test_responsible_is_granted_role_manager_when_responsible_modified(self, browser):
        self.login(self.manager, browser)
        data = {"responsible": {'token': "nicole.kohler"}}
        browser.open(self.dossier, json.dumps(data), method="PATCH", headers=self.api_headers)

        self.assertEqual('nicole.kohler', IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': ['Role Manager'],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': 'nicole.kohler'},
            assignments[0])

        data = {"responsible": {'token': "kathi.barfuss"}}
        browser.open(self.dossier, json.dumps(data), method="PATCH", headers=self.api_headers)

        self.assertEqual('kathi.barfuss', IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': ['Role Manager'],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': 'kathi.barfuss'},
            assignments[0])

    @browsing
    def test_role_manager_permission_is_needed_to_change_responsible(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertEqual('robert.ziegler', IDossier(self.dossier).responsible)

        data = {"responsible": {'token': "nicole.kohler"}}
        with browser.expect_http_error(code=403):
            browser.open(self.dossier, json.dumps(data),
                         method="PATCH", headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'changing_responsible_disallowed',
             u'translated_message': u'Insufficient privileges to modify the responsible.',
             u'type': u'Forbidden'},
            browser.json)

        # dossier_responsible does not have the role manager role, because
        # the feature is not active when the fixture is generated.
        self.dossier.give_permissions_to_responsible()
        browser.open(self.dossier, json.dumps(data),
                     method="PATCH", headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertEqual('nicole.kohler', IDossier(self.dossier).responsible)
