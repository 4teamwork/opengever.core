from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import SolrIntegrationTestCase
import json


class TestGrantDossierManagerToResponsibleFeature(SolrIntegrationTestCase):

    features = (
        'grant_dossier_manager_to_responsible',
    )

    def get_assignments_via_responsible(self, obj):
        manager = RoleAssignmentManager(obj)
        return manager.get_assignments_by_cause(ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE)

    @browsing
    def test_responsible_is_granted_dossier_manager_when_dossier_created(self, browser):
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
             'roles': [
                'Reader',
                'Editor',
                'Contributor',
                'Reviewer',
                'Publisher',
                'DossierManager'
             ],
             'reference': Oguid.for_object(dossier).id,
             'principal': self.regular_user.id},
            assignments[0])

    @browsing
    def test_responsible_is_granted_dossier_manager_when_responsible_modified(self, browser):
        self.login(self.manager, browser)
        data = {"responsible": {'token': self.administrator.id}}
        browser.open(self.dossier, json.dumps(data), method="PATCH", headers=self.api_headers)

        self.assertEqual(self.administrator.id, IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': [
                'Reader',
                'Editor',
                'Contributor',
                'Reviewer',
                'Publisher',
                'DossierManager'
             ],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': self.administrator.id},
            assignments[0])

        data = {"responsible": {'token': self.regular_user.id}}
        browser.open(self.dossier, json.dumps(data), method="PATCH", headers=self.api_headers)

        self.assertEqual(self.regular_user.id, IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)

        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': [
                'Reader',
                'Editor',
                'Contributor',
                'Reviewer',
                'Publisher',
                'DossierManager'
             ],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': self.regular_user.id},
            assignments[0])

    @browsing
    def test_protect_dossier_permission_is_needed_to_change_responsible(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertEqual('robert.ziegler', IDossier(self.dossier).responsible)

        data = {"responsible": {'token': self.administrator.id}}
        with browser.expect_http_error(code=403):
            browser.open(self.dossier, json.dumps(data),
                         method="PATCH", headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'changing_responsible_disallowed',
             u'translated_message': u'Insufficient privileges to modify the responsible.',
             u'type': u'Forbidden'},
            browser.json)

        # dossier_responsible does not have the dossier manager role, because
        # the feature is not active when the fixture is generated.
        IProtectDossier(self.dossier).protect()
        browser.open(self.dossier, json.dumps(data),
                     method="PATCH", headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertEqual(self.administrator.id, IDossier(self.dossier).responsible)

    @browsing
    def test_keeps_dossier_protection_if_responsible_changes(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier')
                         .titled(u'Dossier A')
                         .within(self.leaf_repofolder)
                         .having(responsible=self.dossier_responsible.getId()))

        self.assertEqual(
            (
                (
                    self.dossier_responsible.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                        'Owner'
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        data = {'reading': [self.regular_user.getId()]}
        browser.open(dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(
            (
                (
                    self.regular_user.getId(),
                    (
                        'Reader',
                    )
                ),
                (
                    self.dossier_responsible.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                        'Owner'
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        self.assertTrue(IProtectDossier(dossier).is_dossier_protected())

        data = {'responsible': self.administrator.getId()}
        browser.open(dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(
            (
                (
                    self.administrator.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                    )
                ),
                (
                    self.regular_user.getId(),
                    (
                        'Reader',
                    )
                ),
                (
                    self.dossier_responsible.getId(),
                    (
                        'Owner',
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        self.assertTrue(IProtectDossier(dossier).is_dossier_protected())

    @browsing
    def test_unprotecting_dossier_keeps_dossier_manager_permissions(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier')
                         .titled(u'Dossier A')
                         .within(self.leaf_repofolder)
                         .having(
                             responsible=self.dossier_responsible.getId(),
                             reading=[self.regular_user.getId()]))

        self.assertEqual(
            (
                (
                    self.regular_user.getId(),
                    (
                        'Reader',
                    )
                ),
                (
                    self.dossier_responsible.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                        'Owner'
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        self.assertTrue(IProtectDossier(dossier).is_dossier_protected())

        data = {'reading': []}
        browser.open(dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(
            (
                (
                    self.dossier_responsible.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                        'Owner'
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        self.assertFalse(IProtectDossier(dossier).is_dossier_protected())

    @browsing
    def test_manually_change_dossier_manager_is_not_possible(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier')
                         .titled(u'Dossier A')
                         .within(self.leaf_repofolder)
                         .having(
                             responsible=self.dossier_responsible.getId(),
                         ))

        data = {'dossier_manager': self.administrator.getId()}
        browser.open(dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(
            (
                (
                    self.dossier_responsible.getId(),
                    (
                        'Publisher',
                        'DossierManager',
                        'Editor',
                        'Reader',
                        'Contributor',
                        'Reviewer',
                        'Owner'
                    )
                ),
            ),
            dossier.get_local_roles()
        )

        self.assertEqual(self.dossier_responsible.getId(),
                         IProtectDossier(dossier).dossier_manager)

    @browsing
    def test_transfer_dossier_updates_dossier_protection(self, browser):
        self.login(self.administrator, browser=browser)
        IProtectDossier(self.dossier).protect()

        self.assertEqual(self.dossier_responsible.getId(),
                         IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)

        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': [
                'Reader',
                'Editor',
                'Contributor',
                'Reviewer',
                'Publisher',
                'DossierManager'
             ],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': self.dossier_responsible.id},
            assignments[0])

        browser.open(self.dossier.absolute_url() + '/@transfer-dossier', method='POST',
                     headers=self.api_headers, data=json.dumps(
                         {"old_userid": self.dossier_responsible.getId(),
                          "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), IDossier(self.dossier).responsible)

        assignments = self.get_assignments_via_responsible(self.dossier)

        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 8,
             'roles': [
                'Reader',
                'Editor',
                'Contributor',
                'Reviewer',
                'Publisher',
                'DossierManager'
             ],
             'reference': Oguid.for_object(self.dossier).id,
             'principal': self.meeting_user.getId()},
            assignments[0])
