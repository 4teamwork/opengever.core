from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.globalindex.oguid import Oguid
from opengever.testing import FunctionalTestCase


class TestDossier(FunctionalTestCase):

    def setUp(self):
        super(TestDossier, self).setUp()
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        self.dossier = create(Builder('dossier').within(folder))

    def test_proposal_can_be_added(self):
        proposal = create(Builder('proposal').within(self.dossier))
        self.assertEqual('proposal-1', proposal.getId())

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)

    @browsing
    def test_proposal_can_be_created_in_browser(self, browser):
        proposal = create(Builder('proposal').within(self.dossier))
        browser.login().open(proposal)

        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Proposal': u'My pr\xf6posal'
            }).submit()

        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)

        proposal = browser.context
        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual(u'A pr\xf6posal', model.title)
        self.assertEqual(u'My pr\xf6posal', model.initial_position)
