from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
import json


class GeverRelationChoiceFieldDeserializer(IntegrationTestCase):

    @browsing
    def test_relation_by_url_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.dossier.absolute_url(),
            method='PATCH',
            data=json.dumps(
                {'relatedDossier': [self.empty_dossier.absolute_url()]}
            ),
            headers=self.api_headers)

        self.assertEquals(
            [self.empty_dossier],
            [rel.to_object for rel in IDossier(self.dossier).relatedDossier])

    @browsing
    def test_relation_by_path_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        relative_path = self.empty_dossier.absolute_url_path().replace('/plone', '')
        browser.open(
            self.dossier.absolute_url(),
            method='PATCH',
            data=json.dumps(
                {'relatedDossier': [relative_path]}
            ),
            headers=self.api_headers)

        self.assertEquals(
            [self.empty_dossier],
            [rel.to_object for rel in IDossier(self.dossier).relatedDossier])

    @browsing
    def test_relation_by_oguid_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            self.dossier.absolute_url(),
            method='PATCH',
            data=json.dumps(
                {'relatedDossier': [Oguid.for_object(self.empty_dossier).id]}
            ),
            headers=self.api_headers)

        self.assertEquals(
            [self.empty_dossier],
            [rel.to_object for rel in IDossier(self.dossier).relatedDossier])

    @browsing
    def test_relation_to_object_inside_protected_dossier_is_possible(self, browser):
        self.login(self.administrator, browser=browser)
        subdossier = create(Builder('dossier')
                            .titled(u'Sub')
                            .within(self.protected_dossier))
        RoleAssignmentManager(subdossier).add_or_update_assignments(
            [SharingRoleAssignment(self.regular_user.id, ['Editor'])])
        doc = create(Builder('document')
                     .titled(u'doc')
                     .within(subdossier))

        self.login(self.regular_user, browser=browser)
        browser.open(
            self.document.absolute_url(),
            method='PATCH',
            data=json.dumps(
                {'relatedItems': [doc.absolute_url()]}
            ),
            headers=self.api_headers)

        self.assertEquals([doc], self.document.related_items())
