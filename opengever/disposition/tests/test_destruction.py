from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.disposition.interfaces import IAppraisal
from opengever.testing import IntegrationTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestDestruction(IntegrationTestCase):

    def close_disposition(self):
        with elevated_privileges():
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraise')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-dispose')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-archive')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-close')

    def test_removed_dossiers_are_added_to_destroyed_dossier_list(self):
        self.login(self.regular_user)
        intids = getUtility(IIntIds)
        expected = []
        for dossier in (self.offered_dossier_to_archive, self.offered_dossier_to_destroy):
            expected.append(
              {'intid': intids.getId(dossier),
               'title': dossier.title,
               'appraisal': ILifeCycle(dossier).archival_value == ARCHIVAL_VALUE_WORTHY,
               'reference_number': dossier.get_reference_number(),
               'repository_title': safe_unicode(self.leaf_repofolder.Title()),
               'former_state': dossier.get_former_state()})

        self.close_disposition()

        self.assertEquals(expected,
                          list(self.disposition.get_destroyed_dossiers()))

    def test_destroyed_dossier_list_is_persistent(self):
        self.login(self.regular_user)
        self.close_disposition()

        self.assertEquals(PersistentList,
                          type(self.disposition.get_destroyed_dossiers()))
        self.assertEquals(PersistentMapping,
                          type(self.disposition.get_destroyed_dossiers()[0]))

    def test_all_dossiers_get_removed_when_closing_disposition(self):
        self.login(self.regular_user)
        expected_difference = [self.offered_dossier_to_archive,
                               self.offered_dossier_to_destroy]
        content_before = self.leaf_repofolder.listFolderContents()
        self.close_disposition()
        content_after = self.leaf_repofolder.listFolderContents()

        self.assertItemsEqual(expected_difference,
                              set(content_before).difference(set(content_after)))

    def test_unarchived_dossiers_get_removed_when_closing_disposition(self):
        self.login(self.manager)
        expected_difference = [self.offered_dossier_to_archive,
                               self.offered_dossier_to_destroy]

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        content_before = self.leaf_repofolder.listFolderContents()

        ILifeCycle(self.offered_dossier_to_archive).archival_value = ARCHIVAL_VALUE_UNWORTHY
        IAppraisal(self.disposition).initialize(self.offered_dossier_to_archive)

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraised-to-closed')
        content_after = self.leaf_repofolder.listFolderContents()
        self.assertItemsEqual(expected_difference,
                              set(content_before).difference(set(content_after)))


class TestDestroyPermission(IntegrationTestCase):

    def test_destruction_raises_unauthorized_when_dossiers_are_not_archived(self):
        self.login(self.records_manager)

        with self.assertRaises(Unauthorized):
            self.disposition.destroy_dossiers()

        for dossier in self.disposition.get_dossiers():
            api.content.transition(dossier, to_state='dossier-state-archived')

        self.disposition.destroy_dossiers()

    def test_destruction_raises_unauthorized_when_user_has_not_destroy_permission(self):
        self.login(self.archivist)

        for dossier in self.disposition.get_dossiers():
            api.content.transition(dossier, to_state='dossier-state-archived')

        with self.assertRaises(Unauthorized):
            self.disposition.destroy_dossiers()

        self.login(self.records_manager)
        self.disposition.destroy_dossiers()
