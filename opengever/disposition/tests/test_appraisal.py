from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.disposition.interfaces import IAppraisal
from opengever.testing import FunctionalTestCase
from plone.protect import createToken
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json


class TestAppraisal(FunctionalTestCase):

    def setUp(self):
        super(TestAppraisal, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .as_expired()
                               .within(self.repository))

        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')

    def test_added_dossiers(self):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2])
                             .within(self.root))

        self.assertFalse(IAppraisal(disposition).get(self.dossier1))
        self.assertTrue(IAppraisal(disposition).get(self.dossier2))

    @browsing
    def test_is_updated_when_editing_the_dossier_list(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1])
                             .within(self.root))

        browser.login().open(disposition, view='edit')
        browser.fill({'Dossiers': [self.dossier1, self.dossier2]})
        browser.find('Save').click()

        self.assertFalse(IAppraisal(disposition).get(self.dossier1))
        self.assertTrue(IAppraisal(disposition).get(self.dossier2))

    @browsing
    def test_update_appraisal_via_update_view(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2])
                             .within(self.root))

        self.assertFalse(IAppraisal(disposition).get(self.dossier1))

        intid = getUtility(IIntIds).getId(self.dossier1)
        browser.login().open(disposition, view='update_appraisal_view',
                             data={'_authenticator': createToken(),
                                   'dossier-id': json.dumps(intid),
                                   'should_be_archived': json.dumps(True)})

        self.assertTrue(IAppraisal(disposition).get(self.dossier1))
