from ftw.contentstats.interfaces import IStatsKeyFilter
from ftw.contentstats.interfaces import IStatsProvider
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from zope.component import getMultiAdapter


class TestContentStatsIntegration(IntegrationTestCase):

    def test_portal_types_filter(self):
        flt = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsKeyFilter, name='portal_types')

        # Obviously the core GEVER types should be kept
        self.assertTrue(flt.keep('opengever.document.document'))
        self.assertTrue(flt.keep('opengever.dossier.businesscasedossier'))
        self.assertTrue(flt.keep('opengever.task.task'))

        # As well as ftw.mail
        self.assertTrue(flt.keep('ftw.mail.mail'))

        # These uninteresting top level types should be ignored though
        self.assertFalse(flt.keep('opengever.dossier.templatefolder'))
        self.assertFalse(flt.keep('opengever.repository.repositoryroot'))
        self.assertFalse(flt.keep('opengever.inbox.inbox'))
        self.assertFalse(flt.keep('opengever.inbox.yearfolder'))
        self.assertFalse(flt.keep('opengever.inbox.container'))
        self.assertFalse(flt.keep('opengever.contact.contactfolder'))
        self.assertFalse(flt.keep('opengever.meeting.committeecontainer'))

        # Stock Plone types should be skipped as well
        self.assertFalse(flt.keep('ATBooleanCriterion'))
        self.assertFalse(flt.keep('ATCurrentAuthorCriterion'))
        self.assertFalse(flt.keep('ATDateCriteria'))
        self.assertFalse(flt.keep('ATDateRangeCriterion'))
        self.assertFalse(flt.keep('ATListCriterion'))
        self.assertFalse(flt.keep('ATPathCriterion'))
        self.assertFalse(flt.keep('ATRelativePathCriterion'))
        self.assertFalse(flt.keep('ATPortalTypeCriterion'))
        self.assertFalse(flt.keep('ATReferenceCriterion'))
        self.assertFalse(flt.keep('ATSelectionCriterion'))
        self.assertFalse(flt.keep('ATSimpleIntCriterion'))
        self.assertFalse(flt.keep('ATSimpleStringCriterion'))
        self.assertFalse(flt.keep('ATSortCriterion'))
        self.assertFalse(flt.keep('Discussion Item'))
        self.assertFalse(flt.keep('Document'))
        self.assertFalse(flt.keep('Event'))
        self.assertFalse(flt.keep('File'))
        self.assertFalse(flt.keep('Folder'))
        self.assertFalse(flt.keep('Image'))
        self.assertFalse(flt.keep('Link'))
        self.assertFalse(flt.keep('News Item'))
        self.assertFalse(flt.keep('Plone Site'))
        self.assertFalse(flt.keep('TempFolder'))
        self.assertFalse(flt.keep('Topic'))
        self.assertFalse(flt.keep('Collection'))

        # But any potential future type in opengever.* should be kept
        self.assertTrue(flt.keep('opengever.doesnt.exist.just.yet'))

        # The fake portal_type that sums up docs and mails should also be kept
        self.assertTrue(flt.keep('_opengever.document.behaviors.IBaseDocument'))

    def test_review_states_filter(self):
        flt = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsKeyFilter, name='review_states')

        states_to_keep = [
            'contact-state-active',
            'disposition-state-appraised',
            'disposition-state-archived',
            'disposition-state-closed',
            'disposition-state-disposed',
            'disposition-state-in-progress',
            'document-state-draft',
            'document-state-removed',
            'document-state-shadow',
            'dossier-state-active',
            'dossier-state-archived',
            'dossier-state-inactive',
            'dossier-state-offered',
            'dossier-state-resolved',
            'folder-state-active',
            'forwarding-state-closed',
            'forwarding-state-open',
            'forwarding-state-refused',
            'mail-state-active',
            'mail-state-removed',
            'opengever_committee_workflow--STATUS--active',
            'opengever_committee_workflow--STATUS--inactive',
            'opengever_workspace--STATUS--active',
            'opengever_workspace_folder--STATUS--active',
            'proposal-state-active',
            'proposal-state-submitted',
            'repositoryfolder-state-active',
            'repositoryfolder-state-inactive',
            'task-state-cancelled',
            'task-state-in-progress',
            'task-state-open',
            'task-state-planned',
            'task-state-rejected',
            'task-state-resolved',
            'task-state-skipped',
            'task-state-tested-and-closed',
            'tasktemplate-state-active',
            'tasktemplatefolder-state-activ',
            'tasktemplatefolder-state-inactiv',
            'template-state-active',
        ]

        states_to_ignore = [
            # Stock Plone type states
            'external',
            'internal',
            'internally_published',
            'pending',
            'private',
            'published',
            'visible',

            # Uninteresting top level GEVER type states
            'contactfolder-state-active',
            'inbox-state-default',
            'opengever_committeecontainer_workflow--STATUS--active',
            'opengever_workspace_root--STATUS--active',
            'repositoryroot-state-active',
            'templatefolder-state-active',
        ]

        for state in states_to_keep:
            self.assertTrue(flt.keep(state), 'Expected state %r to be kept by filter (was ignored)' % state)

        for state in states_to_ignore:
            self.assertFalse(flt.keep(state), 'Expected state %r to be ignored by filter (was kept)' % state)

        # Collect a list of ALL the currently possible workflow states
        all_possible_workflow_states = set()
        wftool = api.portal.get_tool('portal_workflow')
        for workflow in wftool.objectValues():
            for wfstate in workflow.states.objectIds():
                all_possible_workflow_states.add(wfstate)

        covered_states = set(states_to_keep + states_to_ignore)
        non_existing_states = covered_states - all_possible_workflow_states

        self.assertEqual(
            set(),
            non_existing_states,
            'Found test for one or more non-existent workflow states:\n %r' % non_existing_states,
        )

        self.assertEqual(
            all_possible_workflow_states,
            covered_states,
            'Missing test assertion for one or more states. Please add explicit assertions for the following workflow '
            'states:\n%r' % (all_possible_workflow_states - covered_states),
        )

    def test_checked_out_docs_stats_provider(self):
        self.login(self.regular_user)
        stats_provider = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsProvider, name='checked_out_docs')
        self.assertEqual({'checked_out': 0, 'checked_in': 39}, stats_provider.get_raw_stats())

        self.checkout_document(self.document)
        self.assertEqual({'checked_out': 1, 'checked_in': 38}, stats_provider.get_raw_stats())

    def test_file_mimetypes_provider(self):
        stats_provider = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsProvider, name='file_mimetypes')
        expected_stats = {
            'application/msword': 3,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 3,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 17,
            'message/rfc822': 3,
            'text/plain': 3,
        }
        self.assertEqual(expected_stats, stats_provider.get_raw_stats())

    def test_file_mimetypes_provider_doesnt_return_empty_string_mimetype(self):
        # Relies on self.empty_document being there
        stats_provider = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsProvider, name='file_mimetypes')
        # Shouldn't cause a mimetype key of '' (empty string) to be produced
        self.assertNotIn('', stats_provider.get_raw_stats().keys())

    @browsing
    def test_file_mimetypes_provider_in_view(self, browser):
        browser.login(SITE_OWNER_NAME)
        browser.open(self.portal, view='@@content-stats')
        table = browser.css('#content-stats-file_mimetypes').first
        expected_stats = [
            ['', 'application/msword', '3'],
            ['', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '3'],
            ['', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '17'],
            ['', 'message/rfc822', '3'],
            ['', 'text/plain', '3'],
        ]
        self.assertEqual(expected_stats, table.lists())

    @browsing
    def test_checked_out_docs_stats_provider_in_view(self, browser):
        self.login(self.manager, browser)
        browser.open(view='@@content-stats')
        table = browser.css('#content-stats-checked_out_docs').first
        self.assertEqual([['', 'checked_in', '39'], ['', 'checked_out', '0']], table.lists())

        self.checkout_document(self.document)
        browser.open(self.portal, view='@@content-stats')
        table = browser.css('#content-stats-checked_out_docs').first
        self.assertEqual([['', 'checked_in', '38'], ['', 'checked_out', '1']], table.lists())

    def test_gever_portal_types_contains_base_documents(self):
        stats_provider = getMultiAdapter((self.portal, self.portal.REQUEST), IStatsProvider, name='portal_types')
        stats = stats_provider.get_raw_stats()
        self.assertIn('_opengever.document.behaviors.IBaseDocument', stats)
        documentish_stats = stats['opengever.document.document'] + stats['ftw.mail.mail']
        self.assertEqual(documentish_stats, stats['_opengever.document.behaviors.IBaseDocument'])
