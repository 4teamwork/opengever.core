from datetime import datetime
# from ftw.builder import Builder
# from ftw.builder import create
from ftw.testbrowser import browsing
# from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings  # noqa
# from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
import Missing
from DateTime import DateTime
from ftw.testing import staticuid

FROZEN_NOW = datetime.now()
FROZEN_TODAY = FROZEN_NOW.date()

METADATA_COLUMNS = [
    'CreationDate',
    'Creator',
    'Date',
    'Description',
    'EffectiveDate',
    'ExpirationDate',
    'ModificationDate',
    'Subject',
    'Title',
    'Type',
    'UID',
    'assigned_client',
    'author_name',
    'bumblebee_checksum',
    'checked_out',
    'cmf_uid',
    'commentators',
    'contactid',
    'containing_dossier',
    'containing_subdossier',
    'created',
    'css_icon_class',
    'date_of_completion',
    'deadline',
    'delivery_date',
    'document_author',
    'document_date',
    'effective',
    'email',
    'email2',
    'end',
    'exclude_from_nav',
    'expires',
    'firstname',
    'getContentType',
    'getIcon',
    'getId',
    'getObjSize',
    'getRemoteUrl',
    'id',
    'in_response_to',
    'is_folderish',
    'is_subtask',
    'issuer',
    'last_comment_date',
    'lastname',
    'listCreators',
    'location',
    'meta_type',
    'modified',
    'phone_office',
    'portal_type',
    'predecessor',
    'preselected',
    'public_trial',
    'receipt_date',
    'reference',
    'responsible',
    'retention_expiration',
    'review_state',
    'sequence_number',
    'start',
    'task_type',
    'title_de',
    'title_fr',
    'total_comments',
    'trashed',
]


REPOROOT_METADATA = {
    # 'CreationDate': '2017-12-21T14:07:15+01:00',
    'Creator': 'admin',
    # 'Date': '2017-12-21T14:07:15+01:00',
    'Description': '',
    'EffectiveDate': 'None',
    'ExpirationDate': 'None',
    # 'ModificationDate': '2017-12-21T14:07:15+01:00',
    'Subject': (),
    'Title': None,
    'Type': u'RepositoryRoot',
    'UID': 'uid00000000000000000000000000001',
    'assigned_client': Missing.Value,
    'author_name': Missing.Value,
    'bumblebee_checksum': Missing.Value,
    'checked_out': Missing.Value,
    'cmf_uid': Missing.Value,
    'commentators': (),
    'contactid': Missing.Value,
    'containing_dossier': None,
    'containing_subdossier': '',
    'created': DateTime(FROZEN_NOW),
    'css_icon_class': Missing.Value,
    'date_of_completion': Missing.Value,
    'deadline': Missing.Value,
    'delivery_date': Missing.Value,
    'document_author': Missing.Value,
    'document_date': Missing.Value,
    'effective': DateTime('1969/12/31 00:00:00 GMT+1'),
    'email': Missing.Value,
    'email2': Missing.Value,
    'end': Missing.Value,
    'exclude_from_nav': Missing.Value,
    'expires': DateTime('2499/12/31 00:00:00 GMT+1'),
    'firstname': Missing.Value,
    'getContentType': Missing.Value,
    'getIcon': '',
    'getId': 'peter',
    'getObjSize': '0 KB',
    'getRemoteUrl': Missing.Value,
    'id': 'peter',
    'in_response_to': Missing.Value,
    'is_folderish': True,
    'is_subtask': Missing.Value,
    'issuer': Missing.Value,
    'last_comment_date': None,
    'lastname': Missing.Value,
    'listCreators': ('admin',),
    'location': Missing.Value,
    'meta_type': 'Dexterity Container',
    'modified': DateTime(FROZEN_NOW),
    'phone_office': Missing.Value,
    'portal_type': 'opengever.repository.repositoryroot',
    'predecessor': Missing.Value,
    'preselected': Missing.Value,
    'public_trial': Missing.Value,
    'receipt_date': Missing.Value,
    'reference': Missing.Value,
    'responsible': Missing.Value,
    'retention_expiration': Missing.Value,
    'review_state': 'repositoryroot-state-active',
    'sequence_number': Missing.Value,
    'start': Missing.Value,
    'task_type': Missing.Value,
    'title_de': 'Peter',
    'title_fr': None,
    'total_comments': 0,
    'trashed': False,
}


IGNORED_INDEXES = [
    'commentators',
    'client_id',
    'assigned_client',
    'allowedRolesAndUsers',
    'Subject',
    'Description',
]


class TestRepositoryRootMetadata(IntegrationTestCase):

    def assert_metadata_matches(self, metadata_name, expected, actual):
        if isinstance(expected, DateTime):
            expected._second = int(expected._second)
            expected = str(expected)
            actual = str(actual)

        self.assertEqual(
            expected, actual,
            "Metadata for %r doesn't match. Expected %r, got %r." % (
                metadata_name, expected, actual))

    @staticuid('uid')
    @browsing
    def test_metadata_delegation(self, browser):
        self.login(self.manager, browser)
        with freeze(FROZEN_NOW):
            reporoot = createContentInContainer(
                self.portal,
                'opengever.repository.repositoryroot',
                title_de='Peter',
            )

        brain = obj2brain(reporoot)

        for metadata_name, expected_value in REPOROOT_METADATA.items():
            if expected_value is Missing.Value:
                continue

            actual_value = getattr(brain, metadata_name)

            self.assert_metadata_matches(
                metadata_name, expected_value, actual_value)

            # print '%s: %s,' % (repr(metadata_name), repr(actual_value))
