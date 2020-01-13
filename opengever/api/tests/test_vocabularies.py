from ftw.testbrowser import browsing
from opengever.base.behaviors.classification import IClassification
from opengever.testing import IntegrationTestCase
from plone import api


NON_SENSITIVE_VOCABUALRIES = [
    'Behaviors',
    'classification_classification_vocabulary',
    'classification_privacy_layer_vocabulary',
    'classification_public_trial_vocabulary',
    'cmf.calendar.AvailableEventTypes',
    'collective.quickupload.fileTypeVocabulary',
    'collective.taskqueue.queues',
    'Fields',
    'ftw.keywordwidget.UnicodeKeywordVocabulary',
    'ftw.usermigration.mapping_sources',
    'ftw.usermigration.post_migration_hooks',
    'ftw.usermigration.pre_migration_hooks',
    'Group Ids',
    'http://www.imsglobal.org/vocabularies/iso2788_relations.xml',
    'http://www.imsglobal.org/vocabularies/iso5964_equivalences.xml',
    'Interfaces',
    'lifecycle_archival_value_vocabulary',
    'lifecycle_custody_period_vocabulary',
    'lifecycle_retention_period_vocabulary',
    'opengever.base.ReferenceFormatterVocabulary',
    'opengever.document.document_types',
    'opengever.dossier.container_types',
    'opengever.dossier.participation_roles',
    'opengever.dossier.type_prefixes',
    'opengever.dossier.ValidResolverNamesVocabulary',
    'opengever.journal.manual_entry_categories',
    'opengever.meeting.ActiveCommitteeVocabulary',
    'opengever.meeting.AdHocAgendaItemTemplatesForCommitteeVocabulary',
    'opengever.meeting.CommitteeVocabulary',
    'opengever.meeting.LanguagesVocabulary',
    'opengever.meeting.MeetingTemplateVocabulary',
    'opengever.meeting.MemberVocabulary',
    'opengever.meeting.ProposalTemplatesForCommitteeVocabulary',
    'opengever.meeting.ProposalTemplatesVocabulary',
    'opengever.ogds.base.AssignedClientsVocabulary',
    'opengever.ogds.base.OrgUnitsVocabularyFactory',
    'opengever.ogds.base.OtherAssignedClientsVocabulary',
    'opengever.repository.RestrictedAddableDossiersVocabulary',
    'opengever.task.bidirectional_by_reference',
    'opengever.task.bidirectional_by_value',
    'opengever.task.reminder.TaskReminderOptionsVocabulary',
    'opengever.task.unidirectional_by_reference',
    'opengever.task.unidirectional_by_value',
    'opengever.tasktemplates.active_tasktemplatefolders',
    'opengever.tasktemplates.ResponsibleOrgUnitVocabulary',
    'opengever.tasktemplates.tasktemplates',
    'opengever.workspace.PossibleWorkspaceFolderParticipantsVocabulary',
    'opengever.workspace.RolesVocabulary',
    'plone.app.content.ValidAddableTypes',
    'plone.app.controlpanel.WickedPortalTypes',
    'plone.app.discussion.vocabularies.CaptchaVocabulary',
    'plone.app.discussion.vocabularies.TextTransformVocabulary',
    'plone.app.vocabularies.Actions',
    'plone.app.vocabularies.AllowableContentTypes',
    'plone.app.vocabularies.AllowedContentTypes',
    'plone.app.vocabularies.AvailableContentLanguages',
    'plone.app.vocabularies.AvailableEditors',
    'plone.app.vocabularies.Catalog',
    'plone.app.vocabularies.CommonTimezones',
    'plone.app.vocabularies.Groups',
    'plone.app.vocabularies.ImagesScales',
    'plone.app.vocabularies.Keywords',
    'plone.app.vocabularies.Month',
    'plone.app.vocabularies.MonthAbbr',
    'plone.app.vocabularies.PortalTypes',
    'plone.app.vocabularies.ReallyUserFriendlyTypes',
    'plone.app.vocabularies.Roles',
    'plone.app.vocabularies.Skins',
    'plone.app.vocabularies.SupportedContentLanguages',
    'plone.app.vocabularies.SyndicatableFeedItems',
    'plone.app.vocabularies.SyndicationFeedTypes',
    'plone.app.vocabularies.Timezones',
    'plone.app.vocabularies.UserFriendlyTypes',
    'plone.app.vocabularies.Users',
    'plone.app.vocabularies.Weekdays',
    'plone.app.vocabularies.WeekdaysAbbr',
    'plone.app.vocabularies.WeekdaysShort',
    'plone.app.vocabularies.Workflows',
    'plone.app.vocabularies.WorkflowStates',
    'plone.app.vocabularies.WorkflowTransitions',
    'plone.contentrules.events',
    'plone.formwidget.relations.cmfcontentsearch',
    'plone.schemaeditor.VocabulariesVocabulary',
    'wicked.vocabularies.BaseConfigurationsOptions',
    'wicked.vocabularies.CacheConfigurationsOptions',
]

# This vocabularies are listet by the @vocabularies endpoint but should not be
# tested if they are accessable by the user or not.
IGNORED_VOCABULARIES = [
    'Behaviors',
    'http://www.imsglobal.org/vocabularies/iso2788_relations.xml',
    'http://www.imsglobal.org/vocabularies/iso5964_equivalences.xml',
    'opengever.tasktemplates.tasktemplates',
    'plone.app.content.ValidAddableTypes',
    'wicked.vocabularies.BaseConfigurationsOptions',
]


class TestNonSensitiveVocabularies(IntegrationTestCase):
    """See https://github.com/4teamwork/opengever.core/issues/5449 for
    more information about this tests.
    """

    @browsing
    def test_vocabularies_endpoint_does_not_provide_sensitive_data(self, browser):
        self.login(self.regular_user, browser)

        response = browser.open(
            self.portal.absolute_url() + '/@vocabularies',
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertItemsEqual(
            NON_SENSITIVE_VOCABUALRIES,
            [vocabulary.get('title') for vocabulary in response],
            'Please validate that the newly introduced vocabularies do not contain '
            'protectable entries and update the list of NON_SENSITIVE_VOCABUALRIES.')

    def assert_permission_for_non_sensitive_vocabulaires(self, browser, role):
        self.login(self.regular_user, browser)
        api.user.grant_roles(user=api.user.get_current(), roles=[role])
        browser.raise_http_errors = False
        not_accessable = []

        for vocabulary in NON_SENSITIVE_VOCABUALRIES:
            if vocabulary in IGNORED_VOCABULARIES:
                continue

            browser.open(
                self.portal.absolute_url() + '/@vocabularies/{}'.format(vocabulary),
                method='GET',
                headers=self.api_headers)

            if browser.status_code != 200:
                not_accessable.append((vocabulary, browser.status_code))

        self.assertEqual(
            [], not_accessable,
            "The listed vocabularies are not accessable with {0} role. "
            "Please make sure that every non-sensitive vocabulary is accessable by "
            "a user with {0} role.".format(role))

    @browsing
    def test_all_non_sensitive_vocabularies_are_accessable_by_a_member(self, browser):
        self.assert_permission_for_non_sensitive_vocabulaires(browser, 'Member')

    @browsing
    def test_all_non_sensitive_vocabularies_are_accessable_by_a_contributor(self, browser):
        self.assert_permission_for_non_sensitive_vocabulaires(browser, 'Contributor')


class TestGetVocabularies(IntegrationTestCase):

    @browsing
    def test_get_vocabulary_for_edit(self, browser):
        self.login(self.regular_user, browser)
        url = self.empty_dossier.absolute_url() + '/@vocabularies/opengever.document.document_types'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        self.assertEqual(url, response.get('@id'))
        self.assertEqual(8, response.get('items_total'))
        expected_tokens = [u'contract', u'directive', u'offer', u'protocol',
                           u'question', u'regulations', u'report', u'request']
        self.assertItemsEqual(expected_tokens,
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_get_vocabulary_for_add(self, browser):
        self.login(self.regular_user, browser)
        url = self.empty_dossier.absolute_url() + '/@vocabularies/opengever.document.document/opengever.document.document_types'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        self.assertEqual(url, response.get('@id'))
        self.assertEqual(8, response.get('items_total'))
        expected_tokens = [u'contract', u'directive', u'offer', u'protocol',
                           u'question', u'regulations', u'report', u'request']
        self.assertItemsEqual(expected_tokens,
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_get_restricted_vocabulary_for_add(self, browser):
        self.login(self.regular_user, browser)

        url = self.leaf_repofolder.absolute_url() + '/@vocabularies/opengever.dossier.businesscasedossier/classification_classification_vocabulary'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        field = IClassification['classification']
        field.set(field.interface(self.leaf_repofolder), u'confidential')
        restricted_response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(url, restricted_response.get('@id'))
        self.assertTrue(
            response.get('items_total') > restricted_response.get('items_total'))
        self.assertIn(
            u'unprotected',
            [item.get('token') for item in response.get('items')]
            )
        self.assertNotIn(
            u'unprotected',
            [item.get('token') for item in restricted_response.get('items')]
            )

    @browsing
    def test_get_restricted_vocabulary_for_edit(self, browser):
        self.login(self.regular_user, browser)

        url = self.dossier.absolute_url() + '/@vocabularies/classification_classification_vocabulary'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        field = IClassification['classification']
        field.set(field.interface(self.leaf_repofolder), u'confidential')
        restricted_response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(url, restricted_response.get('@id'))
        self.assertTrue(
            response.get('items_total') > restricted_response.get('items_total'))
        self.assertIn(
            u'unprotected',
            [item.get('token') for item in response.get('items')]
            )
        self.assertNotIn(
            u'unprotected',
            [item.get('token') for item in restricted_response.get('items')]
            )


class TestGetQuerySources(IntegrationTestCase):

    @browsing
    def test_get_querysource_for_edit(self, browser):
        self.login(self.regular_user, browser)
        url = self.empty_dossier.absolute_url() + '/@querysources/responsible?query=nicole'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'nicole.kohler'],
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_get_vocabulary_for_add(self, browser):
        self.login(self.regular_user, browser)
        url = self.leaf_repofolder.absolute_url() + '/@querysources/opengever.dossier.businesscasedossier/responsible?query=nicole'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'nicole.kohler'],
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_get_keywords_querysource_for_edit(self, browser):
        self.login(self.regular_user, browser)
        url = self.empty_dossier.absolute_url() + '/@querysources/keywords?query=secret'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'secret'],
                              [item['token'] for item in response.get('items')])


class TestGetSources(IntegrationTestCase):

    @browsing
    def test_get_source_for_edit(self, browser):
        self.login(self.regular_user, browser)
        url = self.document.absolute_url() + '/@sources/document_type'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(8, response.get('items_total'))
        expected_tokens = [u'contract', u'directive', u'offer', u'protocol',
                           u'question', u'regulations', u'report', u'request']
        self.assertItemsEqual(expected_tokens,
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_get_vocabulary_for_add(self, browser):
        self.login(self.regular_user, browser)
        url = self.empty_dossier.absolute_url() + '/@sources/opengever.document.document/document_type'
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(8, response.get('items_total'))
        expected_tokens = [u'contract', u'directive', u'offer', u'protocol',
                           u'question', u'regulations', u'report', u'request']
        self.assertItemsEqual(expected_tokens,
                              [item['token'] for item in response.get('items')])
