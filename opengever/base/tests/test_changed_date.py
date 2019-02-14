from datetime import date
from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.behaviors.changed import IChanged
from opengever.base.indexes import changed_indexer
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getMultiAdapter
import pytz


FREEZING_TIME = datetime(2018, 4, 30, 0, 0, tzinfo=pytz.UTC)


class TestChangedBehavior(IntegrationTestCase):

    def test_indexer_returns_python_datetime(self):
        self.login(self.manager)
        changed_index = changed_indexer(self.document)()
        self.assertIsInstance(changed_index, datetime)

    def test_setter_transforms_zope_datetime_to_python_datetime(self):
        self.login(self.manager)
        IChanged(self.document).changed = DateTime()
        self.assertIsInstance(IChanged(self.document).changed, datetime)

    def test_setter_requires_timezone_aware_datetime(self):
        self.login(self.manager)
        with self.assertRaises(AssertionError):
            IChanged(self.document).changed = datetime.now()

    def test_setter_normalizes_timezone_to_utc(self):
        self.login(self.manager)
        IChanged(self.document).changed = DateTime()
        self.assertEqual(IChanged(self.document).changed.tzinfo,
                         pytz.UTC)


class TestChangedUpdateBase(IntegrationTestCase):

    def assert_changed_value(self, obj, value):
        self.assertEqual(value, IChanged(obj).changed)
        self.assert_index_and_metadata(value, "changed")


class TestChangedUpdateForDocument(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.regular_user, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.document, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.document, FREEZING_TIME)

    @browsing
    def test_changed_is_updated_when_workflow_status_is_changed(self, browser):
        self.login(self.manager, browser)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.document, transition="document-transition-remove")
        self.assert_changed_value(self.document, FREEZING_TIME)

    def test_document_changed_is_not_modified_on_checkout(self):
        self.login(self.regular_user)
        initial_changed = IChanged(self.document).changed
        with freeze(FREEZING_TIME):
            self.checkout_document(self.document)
        self.assert_changed_value(self.document, initial_changed)

    def test_document_changed_is_modified_on_checkin(self):
        self.login(self.regular_user)
        with freeze(FREEZING_TIME):
            self.checkout_document(self.document)
            self.checkin_document(self.document)
        self.assert_changed_value(self.document, FREEZING_TIME)

    def test_reindexing_does_not_update_changed(self):
        self.login(self.regular_user)
        initial_changed = IChanged(self.document).changed
        self.document.reindexObject()
        self.assert_changed_value(self.document, initial_changed)

    def test_revert_to_version_updates_changed(self):
        self.login(self.regular_user)
        CHECKIN_TIME = datetime(2018, 4, 28, 0, 0, tzinfo=pytz.UTC)
        with freeze(CHECKIN_TIME):
            self.checkout_document(self.document)
            self.checkin_document(self.document)

        self.assert_changed_value(self.document, CHECKIN_TIME)
        with freeze(FREEZING_TIME):
            self.manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                           ICheckinCheckoutManager)
            self.manager.revert_to_version(0)
        self.assert_changed_value(self.document, FREEZING_TIME)

    @browsing
    def test_changed_is_not_updated_when_containing_dossier_is_changed(self, browser):
        self.login(self.regular_user, browser)
        initial_changed = IChanged(self.document).changed
        with freeze(FREEZING_TIME):
            browser.open(self.dossier, view='edit')
            browser.fill({'Title': 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.document, initial_changed)


class TestChangedUpdateForMail(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.regular_user, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.mail_eml, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.mail_eml, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.mail_eml, transition="mail-transition-remove")
        self.assert_changed_value(self.mail_eml, FREEZING_TIME)


class TestChangedUpdateForDossier(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.regular_user, browser)
        IDossier(self.subdossier).responsible = self.regular_user.getUserName()
        with freeze(FREEZING_TIME):
            browser.open(self.subdossier, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.subdossier, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.subdossier, transition="dossier-transition-resolve")
        self.assert_changed_value(self.subdossier, FREEZING_TIME)

    @browsing
    def test_changed_is_not_updated_when_subdossier_is_changed(self, browser):
        self.login(self.regular_user, browser)
        self.dossier_initial_changed = IChanged(self.dossier).changed
        with freeze(FREEZING_TIME):
            browser.open(self.subdossier, view='transition-deactivate', send_authenticator=True)
        self.assert_changed_value(self.subdossier, FREEZING_TIME)
        self.assert_changed_value(self.dossier, self.dossier_initial_changed)

    def test_changed_is_set_when_copy_paste_an_dossier(self):
        self.login(self.regular_user)

        with freeze(FREEZING_TIME):
            new_dossier = api.content.copy(
                source=self.subdossier, target=self.leaf_repofolder)

        self.assert_changed_value(new_dossier, FREEZING_TIME)
        for obj in new_dossier.objectValues():
            self.assert_changed_value(obj, FREEZING_TIME)


class TestChangedUpdateForTask(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        self.set_workflow_state('task-state-open', self.task)
        with freeze(FREEZING_TIME):
            browser.open(self.task, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.task, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(
                obj=self.subtask,
                transition='task-transition-resolved-tested-and-closed')
            self.assert_changed_value(self.subtask, FREEZING_TIME)


class TestChangedUpdateForProposal(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.meeting_user, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.draft_proposal, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.draft_proposal, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.draft_proposal, transition="proposal-transition-submit")
        self.assert_changed_value(self.draft_proposal, FREEZING_TIME)


class TestChangedUpdateForSablonTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.sablon_template, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.sablon_template, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.sablon_template, transition="document-transition-remove")
        self.assert_changed_value(self.sablon_template, FREEZING_TIME)


class TestChangedUpdateForProposalTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.proposal_template, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.proposal_template, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.proposal_template, transition="document-transition-remove")
        self.assert_changed_value(self.proposal_template, FREEZING_TIME)


class TestChangedUpdateForParagraphTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.paragraph_template, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.paragraph_template, FREEZING_TIME)


class TestChangedUpdateForDossierTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.dossiertemplate, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.dossiertemplate, FREEZING_TIME)


class TestChangedUpdateForTaskTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        self.tasktemplate.task_type = "correction"
        with freeze(FREEZING_TIME):
            browser.open(self.tasktemplate, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.tasktemplate, FREEZING_TIME)


class TestChangedUpdateForTaskTemplateFolder(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.tasktemplatefolder, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.tasktemplatefolder, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.tasktemplatefolder,
                                   transition="tasktemplatefolder-transition-activ-inactiv")
        self.assert_changed_value(self.tasktemplatefolder, FREEZING_TIME)


class TestChangedUpdateForPrivateDossier(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.regular_user, browser)
        IDossier(self.private_dossier).responsible = self.regular_user.getUserName()
        with freeze(FREEZING_TIME):
            browser.open(self.private_dossier, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.private_dossier, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.private_dossier, transition="dossier-transition-resolve")
        self.assert_changed_value(self.private_dossier, FREEZING_TIME)


class TestChangedUpdateForContact(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.franz_meier, view='edit')
            browser.fill({"Description": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.franz_meier, FREEZING_TIME)


class TestChangedUpdateForSubmittedProposal(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.committee_responsible, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.submitted_proposal, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.submitted_proposal, FREEZING_TIME)


class TestChangedUpdateForCommittee(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.committee_responsible, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.committee, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.committee, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.committee,
                                   transition="opengever_committee_workflow--TRANSITION--deactivate--active_inactive")
        self.assert_changed_value(self.committee, FREEZING_TIME)


class TestChangedUpdateForMeetingDossier(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.regular_user, browser)
        IDossier(self.meeting_dossier).responsible = self.regular_user.getUserName()
        with freeze(FREEZING_TIME):
            browser.open(self.meeting_dossier, view='edit')
            browser.fill({"Description": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.meeting_dossier, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.meeting_dossier, transition="dossier-transition-resolve")
        self.assert_changed_value(self.meeting_dossier, FREEZING_TIME)


class TestChangedUpdateForMeetingTemplate(TestChangedUpdateBase):

    features = ('meeting',)

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.meeting_template, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.meeting_template, FREEZING_TIME)


class TestChangedUpdateForWorkspace(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.workspace_owner, browser)
        IDossier(self.workspace).responsible = self.workspace_owner.getUserName()
        with freeze(FREEZING_TIME):
            browser.open(self.workspace, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.workspace, FREEZING_TIME)


class TestChangedUpdateForWorkspaceFolder(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.workspace_owner, browser)
        IDossier(self.workspace_folder).responsible = self.workspace_owner.getUserName()
        with freeze(FREEZING_TIME):
            browser.open(self.workspace_folder, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.workspace_folder, FREEZING_TIME)


class TestChangedUpdateForRepositoryFolder(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.branch_repofolder, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.branch_repofolder, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.branch_repofolder, transition="repositoryfolder-transition-inactivate")
        self.assert_changed_value(self.branch_repofolder, FREEZING_TIME)


class TestChangedUpdateForInbox(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.manager, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.inbox, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.inbox, FREEZING_TIME)


class TestChangedUpdateForForwarding(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.administrator, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.inbox_forwarding, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.inbox_forwarding, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(
                obj=self.inbox_forwarding,
                transition="forwarding-transition-reassign",
                transition_params={'responsible': self.regular_user.id,
                                   'responsible_client':'fa'})

        self.assert_changed_value(self.inbox_forwarding, FREEZING_TIME)


class TestChangedUpdateForYearFolder(TestChangedUpdateBase):

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.manager, browser)
        self.yearfolder = create(Builder('yearfolder').within(self.inbox).having(id="2018"))
        with freeze(FREEZING_TIME):
            browser.open(self.yearfolder, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.yearfolder, FREEZING_TIME)


class TestChangedUpdateForDisposition(TestChangedUpdateBase):

    transition_name = "disposition-transition-appraise"

    def setUp(self):
        super(TestChangedUpdateForDisposition, self).setUp()
        with self.login(self.records_manager):
            self.disposition = create(Builder('disposition').having(dossiers=[self.expired_dossier]))

    @browsing
    def test_changed_is_updated_when_metadata_is_changed(self, browser):
        self.login(self.records_manager, browser)
        with freeze(FREEZING_TIME):
            browser.open(self.disposition, view='edit')
            browser.fill({"Title": 'foo'})
            browser.find('Save').click()
        self.assert_changed_value(self.disposition, FREEZING_TIME)

    def test_changed_is_updated_when_workflow_status_is_changed(self):
        self.login(self.manager)
        with freeze(FREEZING_TIME):
            api.content.transition(obj=self.disposition, transition="disposition-transition-appraise")
        self.assert_changed_value(self.disposition, FREEZING_TIME)
