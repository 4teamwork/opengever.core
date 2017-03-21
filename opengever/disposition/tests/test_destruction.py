from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.testing import FunctionalTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestDestruction(FunctionalTestCase):

    def setUp(self):
        super(TestDestruction, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .titled('Anfragen')
                                 .within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 1')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 2')
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .as_expired()
                               .within(self.repository))
        self.dossier3 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 3')
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .as_expired()
                               .within(self.repository))

        intids = getUtility(IIntIds)
        self.dossier_intids = [intids.getId(self.dossier1),
                               intids.getId(self.dossier2),
                               intids.getId(self.dossier3)]

        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')
        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1,
                                                    self.dossier2,
                                                    self.dossier3])
                                  .in_state('disposition-state-archived')
                                  .within(self.root))

        self.disposition.mark_dossiers_as_archived()

    def test_removed_dossiers_are_added_to_destroyed_dossier_list(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        expected = [
            {'intid': self.dossier_intids[0],
             'title': u'D\xf6ssier 1',
             'appraisal': False,
             'reference_number': 'Client1 1 / 1',
             'repository_title': u'1. Anfragen',
             'former_state': u'dossier-state-resolved'},
            {'intid': self.dossier_intids[1],
             'title': u'D\xf6ssier 2',
             'appraisal': True,
             'reference_number': 'Client1 1 / 2',
             'repository_title': u'1. Anfragen',
             'former_state': u'dossier-state-resolved'},
            {'intid': self.dossier_intids[2],
             'title': u'D\xf6ssier 3',
             'appraisal': True,
             'reference_number': 'Client1 1 / 3',
             'repository_title': u'1. Anfragen',
             'former_state': u'dossier-state-resolved'}]

        self.assertEquals(expected,
                          list(self.disposition.get_destroyed_dossiers()))

    def test_destroyed_dossier_list_is_persistent(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        self.assertEquals(PersistentList,
                          type(self.disposition.get_destroyed_dossiers()))
        self.assertEquals(PersistentMapping,
                          type(self.disposition.get_destroyed_dossiers()[0]))

    def test_when_closing_all_dossier_gets_removed(self):
        self.assertEquals(
            [self.dossier1, self.dossier2, self.dossier3],
            self.repository.listFolderContents())

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        self.assertEquals([], self.repository.listFolderContents())


class TestDestroyPermission(FunctionalTestCase):

    def setUp(self):
        super(TestDestroyPermission, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .titled('Anfragen')
                                 .within(self.root))
        self.grant('Records Manager')

    def test_destruction_raises_unauthorized_when_dossiers_is_not_archived(self):
        dossier = create(Builder('dossier')
                         .titled(u'D\xf6ssier 2')
                         .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                         .as_expired()
                         .within(self.repository))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier])
                             .within(self.root))

        with self.assertRaises(Unauthorized):
            disposition.destroy_dossiers()

    def test_destruction_raises_unauthorized_when_user_has_not_destroy_permission(self):
        dossier = create(Builder('dossier')
                         .titled(u'D\xf6ssier 2')
                         .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                         .as_expired()
                         .within(self.repository))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier])
                             .within(self.root))

        self.grant('Archivist', 'Records Manager')
        api.content.transition(obj=disposition,
                               transition='disposition-transition-appraise')
        api.content.transition(obj=disposition,
                               transition='disposition-transition-dispose')
        api.content.transition(obj=disposition,
                               transition='disposition-transition-archive')

        self.grant('Archivist')
        with self.assertRaises(Unauthorized):
            disposition.destroy_dossiers()

        self.grant('Records Manager')
        disposition.destroy_dossiers()


class TestDestructionForNotArchivedDossiers(FunctionalTestCase):

    def setUp(self):
        super(TestDestructionForNotArchivedDossiers, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .titled('Anfragen')
                                 .within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 1')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 2')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .in_state('dossier-state-inactive')
                               .within(self.repository))

        self.grant('Records Manager', 'Contributor')
        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1, self.dossier2])
                                  .in_state('disposition-state-appraised')
                                  .within(self.root))

    def test_dossiers_gets_removed(self):
        self.assertEquals(
            [self.dossier1, self.dossier2],
            self.repository.listFolderContents())

        api.content.transition(
            obj=self.disposition,
            transition='disposition-transition-appraised-to-closed')

        self.assertEquals(
            [],
            self.repository.listFolderContents())
