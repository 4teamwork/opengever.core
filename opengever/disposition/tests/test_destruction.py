from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.testing import FunctionalTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestDestruction(FunctionalTestCase):

    def setUp(self):
        super(TestDestruction, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 1')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 2')
                               .as_expired()
                               .within(self.repository))
        self.dossier3 = create(Builder('dossier')
                               .titled(u'D\xf6ssier 3')
                               .as_expired()
                               .within(self.repository))

        intids = getUtility(IIntIds)
        self.dossier_intids = [intids.getId(self.dossier1),
                               intids.getId(self.dossier2),
                               intids.getId(self.dossier3)]

        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1,
                                                    self.dossier2,
                                                    self.dossier3])
                                  .in_state('disposition-state-archived')
                                  .within(self.root))

        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')
        self.disposition.mark_dossiers_as_archived()

    def test_removed_dossiers_are_added_to_destroyed_dossier_list(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        expected = [
            {'intid': self.dossier_intids[0],
             'title': u'D\xf6ssier 1',
             'appraisal': False,
             'reference_number': 'Client1 1 / 1'},
            {'intid': self.dossier_intids[1],
             'title': u'D\xf6ssier 2',
             'appraisal': True,
             'reference_number': 'Client1 1 / 2'},
            {'intid': self.dossier_intids[2],
             'title': u'D\xf6ssier 3',
             'appraisal': True,
             'reference_number': 'Client1 1 / 3'}]

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
