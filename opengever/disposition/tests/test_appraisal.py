from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_PROMPT
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNCHECKED
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone.protect import createToken
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json


class TestAppraisal(IntegrationTestCase):

    @browsing
    def test_added_dossiers(self, browser):
        self.login(self.records_manager, browser=browser)
        self.set_workflow_state("dossier-state-resolved", self.dossier, self.empty_dossier)
        self.dossier1 = create(Builder('dossier')
                               .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                               .as_expired()
                               .within(self.leaf_repofolder))
        self.dossier2 = create(Builder('dossier')
                               .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                               .as_expired()
                               .within(self.leaf_repofolder))
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_WORTHY
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_UNCHECKED
        ILifeCycle(self.dossier).archival_value = ARCHIVAL_VALUE_PROMPT

        dossiers = [self.dossier, self.expired_dossier,
                    self.empty_dossier, self.inactive_dossier, self.dossier1]
        disposition = create(Builder('disposition').having(dossiers=dossiers)
                             .within(self.repository_root))

        self.assertItemsEqual(dossiers, disposition.get_dossiers())
        self.assertFalse(IAppraisal(disposition).get(self.dossier1))
        self.assertTrue(IAppraisal(disposition).get(self.expired_dossier))
        self.assertIsNone(IAppraisal(disposition).get(self.empty_dossier))
        self.assertIsNone(IAppraisal(disposition).get(self.dossier2))
        self.assertIsNone(IAppraisal(disposition).get(self.dossier))

    def test_inactive_dossiers_are_always_not_archival_worthy(self):
        self.login(self.records_manager)
        self.set_workflow_state("dossier-state-inactive", self.empty_dossier)
        ILifeCycle(self.inactive_dossier).archival_value = ARCHIVAL_VALUE_WORTHY
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_SAMPLING

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.inactive_dossier, self.expired_dossier])
                             .within(self.repository_root))

        self.assertFalse(IAppraisal(disposition).get(self.inactive_dossier))
        self.assertFalse(IAppraisal(disposition).get(self.empty_dossier))

    @browsing
    def test_is_updated_when_editing_the_dossier_list(self, browser):
        self.login(self.records_manager, browser=browser)
        self.set_workflow_state("dossier-state-resolved", self.empty_dossier)
        IDossier(self.empty_dossier).end = date(2000, 1, 1)
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_WORTHY
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.expired_dossier])
                             .within(self.repository_root))

        self.assertEqual([self.expired_dossier], disposition.get_dossiers())

        browser.open(disposition, view='edit')
        browser.fill({'Dossiers': [self.expired_dossier, self.empty_dossier]})
        browser.find('Save').click()

        self.assertEqual([self.expired_dossier, self.empty_dossier],
                         disposition.get_dossiers())

    @browsing
    def test_update_appraisal_via_update_view(self, browser):
        self.login(self.records_manager, browser=browser)
        self.set_workflow_state("dossier-state-resolved", self.empty_dossier)
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_SAMPLING
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.expired_dossier, self.empty_dossier])
                             .within(self.repository_root))

        self.assertFalse(IAppraisal(disposition).get(self.expired_dossier))
        self.assertFalse(IAppraisal(disposition).get(self.empty_dossier))

        intid = getUtility(IIntIds).getId(self.expired_dossier)
        browser.open(disposition, view='update_appraisal_view',
                     data={'_authenticator': createToken(),
                           'dossier-id': json.dumps(intid),
                           'should_be_archived': json.dumps(True)})

        self.assertTrue(IAppraisal(disposition).get(self.expired_dossier))
        self.assertFalse(IAppraisal(disposition).get(self.empty_dossier))

    @browsing
    def test_update_appraisal_for_multiple_dossiers_via_update_view(self, browser):
        self.login(self.records_manager, browser=browser)
        self.set_workflow_state("dossier-state-resolved", self.empty_dossier)
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_SAMPLING
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY

        repository2 = create(Builder('repository').within(self.repository_root))
        dossier1 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(repository2))
        dossier2 = create(Builder('dossier')
                          .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                          .as_expired()
                          .within(repository2))

        disposition = create(Builder('disposition')
                             .within(self.repository_root)
                             .having(dossiers=[self.expired_dossier, self.empty_dossier,
                                               dossier1, dossier2]))

        self.assertFalse(IAppraisal(disposition).get(self.expired_dossier))
        self.assertFalse(IAppraisal(disposition).get(self.empty_dossier))
        self.assertFalse(IAppraisal(disposition).get(dossier1))
        self.assertFalse(IAppraisal(disposition).get(dossier2))

        intids = getUtility(IIntIds)
        dossier_ids = [intids.getId(self.expired_dossier),
                       intids.getId(dossier1),
                       intids.getId(dossier2)]
        browser.open(disposition, view='update_appraisal_view',
                     data={'_authenticator': createToken(),
                           'dossier-ids': json.dumps(dossier_ids),
                           'should_be_archived': json.dumps(True)})

        self.assertTrue(IAppraisal(disposition).get(self.expired_dossier))
        self.assertFalse(IAppraisal(disposition).get(self.empty_dossier))
        self.assertTrue(IAppraisal(disposition).get(dossier1))
        self.assertTrue(IAppraisal(disposition).get(dossier2))

    def test_appraisal_is_incomplete_when_not_all_dossiers_are_appraised(self):
        self.login(self.records_manager)
        self.set_workflow_state("dossier-state-resolved", self.dossier, self.empty_dossier)
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_WORTHY
        ILifeCycle(self.empty_dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY
        ILifeCycle(self.dossier).archival_value = ARCHIVAL_VALUE_SAMPLING

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.expired_dossier,
                                               self.empty_dossier,
                                               self.dossier])
                             .within(self.repository_root))

        appraisal = IAppraisal(disposition)
        self.assertFalse(appraisal.is_complete())

        appraisal.update(dossier=self.dossier, archive=True)
        self.assertTrue(appraisal.is_complete())
