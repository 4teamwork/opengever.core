from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_PROMPT
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNCHECKED
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

        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer', 'Records Manager')

    def test_added_dossiers(self):
        dossier3 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(self.repository))
        dossier4 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_UNCHECKED)
                          .as_expired()
                          .within(self.repository))
        dossier5 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_PROMPT)
                          .as_expired()
                          .within(self.repository))

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2,
                                               dossier3, dossier4, dossier5])
                             .within(self.root))

        self.assertFalse(IAppraisal(disposition).get(self.dossier1))
        self.assertTrue(IAppraisal(disposition).get(self.dossier2))
        self.assertIsNone(IAppraisal(disposition).get(dossier3))
        self.assertIsNone(IAppraisal(disposition).get(dossier4))
        self.assertIsNone(IAppraisal(disposition).get(dossier5))

    def test_inactive_dossiers_are_always_not_archival_worthy(self):
        dossier1 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .in_state('dossier-state-inactive')
                          .within(self.repository))
        dossier2 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                          .as_expired()
                          .in_state('dossier-state-inactive')
                          .within(self.repository))

        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier1, dossier2])
                             .within(self.root))

        self.assertFalse(IAppraisal(disposition).get(dossier1))
        self.assertFalse(IAppraisal(disposition).get(dossier2))

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

    @browsing
    def test_update_appraisal_for_multiple_dossiers_via_update_view(self, browser):
        repository2 = create(Builder('repository').within(self.root))
        dossier3 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(repository2))
        dossier4 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(repository2))
        disposition = create(Builder('disposition')
                             .within(self.root)
                             .having(dossiers=[self.dossier1, self.dossier2,
                                               dossier3, dossier4]))

        intids = getUtility(IIntIds)
        dossier_ids = [intids.getId(self.dossier1),
                       intids.getId(dossier3),
                       intids.getId(dossier4)]
        browser.login().open(disposition, view='update_appraisal_view',
                             data={'_authenticator': createToken(),
                                   'dossier-ids': json.dumps(dossier_ids),
                                   'should_be_archived': json.dumps(True)})

        self.assertTrue(IAppraisal(disposition).get(self.dossier1))
        self.assertTrue(IAppraisal(disposition).get(dossier3))
        self.assertTrue(IAppraisal(disposition).get(dossier4))

    def test_appraisal_is_in_complete_when_not_all_dossiers_are_appraised(self):
        dossier3 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(self.repository))

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1,
                                               self.dossier2,
                                               dossier3])
                             .within(self.root))

        appraisal = IAppraisal(disposition)
        self.assertFalse(appraisal.is_complete())

        appraisal.update(dossier=dossier3, archive=True)
        self.assertTrue(appraisal.is_complete())
