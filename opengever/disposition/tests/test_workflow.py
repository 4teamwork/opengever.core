from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import obj2paths
from plone import api
from plone.protect import createToken


class TestDispositionWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionWorkflow, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))

    def test_initial_state_is_in_progress(self):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2])
                             .within(self.root))

        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(disposition))
