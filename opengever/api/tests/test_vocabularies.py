from collective.elephantvocabulary.interfaces import IElephantVocabulary
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.schema.sources import get_field_by_name
from opengever.ogds.auth.testing import DisabledGroupPlugins
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.ou_selector import CURRENT_ORG_UNIT_KEY
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.workspace import WHITELISTED_TEAMRAUM_PORTAL_TYPES
from opengever.workspace import WHITELISTED_TEAMRAUM_VOCABULARIES
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


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
    'opengever.dossier.DocumentTemplatesVocabulary',
    'opengever.dossier.DossierTemplatesVocabulary',
    'opengever.dossier.dossier_types',
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
    'opengever.ogds.base.all_admin_units',
    'opengever.ogds.base.all_other_admin_units',
    'opengever.ogds.base.AssignedClientsVocabulary',
    'opengever.ogds.base.OrgUnitsVocabularyFactory',
    'opengever.ogds.base.OtherAssignedClientsVocabulary',
    'opengever.propertysheets.PropertySheetAssignmentsVocabulary',
    'opengever.task.attachable_documents_vocabulary',
    'opengever.task.bidirectional_by_reference',
    'opengever.task.bidirectional_by_value',
    'opengever.task.reminder.TaskReminderOptionsVocabulary',
    'opengever.task.unidirectional_by_reference',
    'opengever.task.unidirectional_by_value',
    'opengever.tasktemplates.active_tasktemplatefolders',
    'opengever.tasktemplates.tasktemplates',
    'opengever.workspace.WorkspaceContentMembersVocabulary',
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

# These vocabularies are listed by the @vocabularies endpoint but should not be
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

    def setUp(self):
        # XXX: Move this onto the layer once remaining tests are fixed.

        # Disable groupEnumeration for source_groups to avoid MultiplePrincipalError.
        self.disabled_source_groups = DisabledGroupPlugins(self.layer['portal'].acl_users)
        self.disabled_source_groups.__enter__()
        super(TestNonSensitiveVocabularies, self).setUp()

    def tearDown(self):
        super(TestNonSensitiveVocabularies, self).tearDown()
        self.disabled_source_groups.__exit__(None, None, None)

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
            'protectable entries for GEVER nor teamraum and update the list of '
            'NON_SENSITIVE_VOCABUALRIES.')

    def assert_permission_for_non_sensitive_vocabulaires(self, browser, role=None, user=None):
        if not user:
            user = self.regular_user

        self.login(user, browser)

        if role:
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
    def test_all_non_sensitive_vocabularies_are_accessable_by_an_authenticated_user(self, browser):
        self.assert_permission_for_non_sensitive_vocabulaires(browser, user=self.foreign_contributor)

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


class TestGetQuerySources(IntegrationTestCase):

    @browsing
    def test_get_querysource_for_edit(self, browser):
        self.login(self.regular_user, browser)
        url = self.query_source_url(
            self.empty_dossier, 'responsible', query='nicole')
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
        url = self.query_source_url(
            self.leaf_repofolder,
            'responsible',
            add='opengever.dossier.businesscasedossier',
            query='nicole',
        )
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
        url = self.query_source_url(
            self.empty_dossier, 'keywords', query='secret')
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'secret'],
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_query_source_by_token_for_add(self, browser):
        self.login(self.secretariat_user, browser)
        url = self.query_source_url(
            self.inbox,
            'responsible',
            add='opengever.inbox.forwarding',
            token='inbox:fa',
        )
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'inbox:fa'],
                              [item['token'] for item in response.get('items')])

    @browsing
    def test_query_source_by_token_for_edit(self, browser):
        self.login(self.secretariat_user, browser)
        url = self.query_source_url(
            self.task,
            'issuer',
            token='nicole.kohler',
        )
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
    def test_query_source_returns_empty_list_for_inexisting_token(self, browser):
        self.login(self.regular_user, browser)
        url = self.query_source_url(
            self.dossier,
            'responsible',
            token='i.do.not.exist',
        )
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(0, response.get('items_total'))
        self.assertItemsEqual([], response.get('items'))

    @browsing
    def test_query_source_disallows_no_query_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = self.query_source_url(
            self.dossier,
            'responsible',
        )
        with browser.expect_http_error(400):
            browser.open(
                url,
                method='GET',
                headers=self.api_headers,
            )
        self.assertEqual(
            {u'error':
                {u'message': u'Enumerating querysources is not supported. '
                              'Please search the source using the ?query= or '
                              '?token = QS parameters',
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_query_source_disallows_both_query_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = self.query_source_url(
            self.dossier,
            'responsible',
            query='foo',
            token='bar',
        )
        with browser.expect_http_error(400):
            browser.open(
                url,
                method='GET',
                headers=self.api_headers,
            )
        self.assertEqual(
            {u'error':
                {u'message': u'Please only search the source using either '
                               'the ?query= or ?token = QS parameters, using '
                               'both parameters at the same time is '
                               'unsupported',
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_add_forwarding_responsible_query_source_falls_back_to_current_org_unit_cookie(self, browser):
        self.login(self.secretariat_user, browser)
        url = self.query_source_url(
            self.inbox,
            'responsible',
            add='opengever.inbox.forwarding',
            query='nicole',
        )

        # set the cookie which is uses as a fallback
        driver = browser.get_driver()
        driver.requests_session.cookies.set(CURRENT_ORG_UNIT_KEY, 'fa')

        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json

        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))
        self.assertItemsEqual([u'fa:nicole.kohler'],
                              [item['token'] for item in response.get('items')])


class TestGetQuerySourcesSolr(SolrIntegrationTestCase):

    @browsing
    def test_get_task_issuer_non_ascii_char_handling(self, browser):
        self.login(self.regular_user, browser)
        url = self.query_source_url(self.task, 'issuer', query=u'k\xf6vin')
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        self.assertEqual(url, response.get('@id'))
        self.assertEqual(0, response.get('items_total'))

    @browsing
    def test_get_task_issuer_escaping_for_solr(self, browser):
        self.login(self.secretariat_user, browser)

        user = User.get(self.regular_user.id)
        user.firstname = 'Super:franz'

        self.commit_solr()

        url = self.query_source_url(self.task, 'issuer', query=u'Super:fr')
        response = browser.open(
            url,
            method='GET',
            headers=self.api_headers,
        ).json
        self.assertEqual(url, response.get('@id'))
        self.assertEqual(1, response.get('items_total'))


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


class TestElephantVocabularies(IntegrationTestCase):

    @browsing
    def test_fields_with_elephant_vocabularies_are_serialized_properly(self, browser):
        self.login(self.regular_user, browser)

        schemata = iterSchemata(self.document)
        document_type_field = get_field_by_name('document_type', schemata)
        vocabulary = document_type_field.vocabulary(self.document)

        self.assertTrue(
            IElephantVocabulary.providedBy(vocabulary),
            "Make sure that the tested field is really an elephant vocabulary.")

        browser.open(self.document, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'token': u'contract', u'title': u'Contract'},
            browser.json[document_type_field.getName()])


class TestGetSourcesInTeamraum(IntegrationTestCase):

    features = ('workspace', )

    @browsing
    def test_only_sources_of_whitelisted_portal_types_are_allowed(self, browser):
        self.login(self.regular_user, browser=browser)

        portal_type = 'opengever.dossier.businesscasedossier'
        url = '{}/@sources/{}/filing_prefix'.format(
            self.portal.absolute_url(), portal_type)

        self.assertNotIn(portal_type, WHITELISTED_TEAMRAUM_PORTAL_TYPES)

        with browser.expect_http_error(reason='Not Found'):
            browser.open(url, headers=self.api_headers)

        self.deactivate_feature('workspace')

        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)


class TestGetQuerySourcesInTeamraum(IntegrationTestCase):

    features = ('workspace', )

    @browsing
    def test_only_querysources_of_whitelisted_portal_types_are_allowed(self, browser):
        self.login(self.regular_user, browser=browser)

        portal_type = 'opengever.dossier.businesscasedossier'
        url = '{}/@querysources/{}/responsible?query=foo'.format(
            self.portal.absolute_url(), portal_type)

        self.assertNotIn(portal_type, WHITELISTED_TEAMRAUM_PORTAL_TYPES)

        with browser.expect_http_error(reason='Not Found'):
            browser.open(url, headers=self.api_headers)

        self.deactivate_feature('workspace')

        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)


class TestGetVocabulariesInTeamraum(IntegrationTestCase):

    features = ('workspace', )

    @browsing
    def test_vocabularies_returns_a_list_of_all_visible_vocabularies(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@vocabularies'.format(self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertItemsEqual(
            WHITELISTED_TEAMRAUM_VOCABULARIES,
            [item.get('title') for item in browser.json])

    @browsing
    def test_raises_not_found_for_not_visible_vocabularies(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@vocabularies/plone.app.vocabularies.Users'.format(
            self.portal.absolute_url())

        self.deactivate_feature('workspace')
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.activate_feature('workspace')
        with browser.expect_http_error(404):
            browser.open(url, headers=self.api_headers)


class TestAllOtherAdminUnitsVocabulary(IntegrationTestCase):

    @browsing
    def test_all_other_admin_units_excludes_current_unit(self, browser):
        create(Builder('admin_unit').id('unit-2'))
        create(Builder('admin_unit').id('unit-3'))
        create(Builder('admin_unit').id('unit-4').having(enabled=False))
        create(Builder('admin_unit').id('unit-5').having(hidden=True))

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = u'unit-3'

        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@vocabularies/opengever.ogds.base.all_other_admin_units'
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(
            [u'plone', u'unit-2'],
            [admin_unit.get('token') for admin_unit in browser.json.get('items')]
        )


class TestAllAdminUnitsVocabulary(IntegrationTestCase):

    @browsing
    def test_all_admin_units_excludes_current_unit(self, browser):
        create(Builder('admin_unit').id('unit-2'))
        create(Builder('admin_unit').id('unit-3'))
        create(Builder('admin_unit').id('unit-4').having(enabled=False))
        create(Builder('admin_unit').id('unit-5').having(hidden=True))

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = u'unit-3'

        self.login(self.regular_user, browser)
        url = self.portal.absolute_url() + '/@vocabularies/opengever.ogds.base.all_admin_units'
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(
            [u'plone', u'unit-2', 'unit-3'],
            [admin_unit.get('token') for admin_unit in browser.json.get('items')]
        )
