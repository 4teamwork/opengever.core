from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_PROMPT
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.testing import FunctionalTestCase
from plone import api


class TestDispositionWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionWorkflow, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_PROMPT)
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                               .within(self.repository))
        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1, self.dossier2])
                                  .within(self.root))

        self.grant('Records Manager')

    def test_initial_state_is_in_progress(self):
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_when_appraising_final_archival_value_is_stored_on_dossier(self):
        IAppraisal(self.disposition).update(
            dossier=self.dossier1, archive=False)
        IAppraisal(self.disposition).update(
            dossier=self.dossier2, archive=True)

        api.content.transition(
            self.disposition, transition='disposition-transition-appraise')

        self.assertEquals(
            ARCHIVAL_VALUE_UNWORTHY, ILifeCycle(self.dossier1).archival_value)
        self.assertEquals(
            ARCHIVAL_VALUE_WORTHY, ILifeCycle(self.dossier2).archival_value)
