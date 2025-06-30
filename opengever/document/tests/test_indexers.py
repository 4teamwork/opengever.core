from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.document.approvals import APPROVED_IN_CURRENT_VERSION
from opengever.document.approvals import APPROVED_IN_OLDER_VERSION
from opengever.document.approvals import IApprovalList
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.indexers import DefaultDocumentIndexer
from opengever.document.indexers import filename as filename_indexer
from opengever.document.indexers import metadata
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentIndexer
from opengever.document.versioner import Versioner
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.app.relationfield.event import update_behavior_relations
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import datetime
import pytz


class TestDocumentIndexers(FunctionalTestCase):

    def test_sortable_title_indexer_accomodates_padding_for_five_numbers(self):
        numeric_part = "1 2 3 4 5"
        alphabetic_part = u"".join(["a" for i in range(CONTENT_TITLE_LENGTH
                                                       - len(numeric_part))])
        title = numeric_part + alphabetic_part
        document = create(Builder("document").titled(title))

        self.assertEquals(
            '0001 0002 0003 0004 0005' + alphabetic_part,
            index_data_for(document).get('sortable_title'))

    def test_author_indexers(self):
        """check the author indexers."""

        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One", document_author=u'Hugo Boss',
            document_date=datetime.date(2011, 1, 1))

        self.assertEquals(obj2brain(doc1).document_author, 'Hugo Boss')

        # without a author
        doc1.document_author = None
        doc1.reindexObject()

        self.assertEquals(obj2brain(doc1).document_author, None)

        # with a non-ascii characters including author

        doc1.document_author = u'H\xfcgo B\xf6ss'
        doc1.reindexObject()

        self.assertEquals(
            obj2brain(doc1).document_author, 'H\xc3\xbcgo B\xc3\xb6ss')

    def test_document_type_indexer(self):
        document = create(Builder("document"))
        self.assertEqual(index_data_for(document)['document_type'], None)

        IDocumentMetadata(document).document_type = "question"
        document.reindexObject()
        self.assertEqual(index_data_for(document)['document_type'], "question")

    def test_filesize_indexers(self):
        document = create(
            Builder("document")
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(7, index_data_for(document).get('filesize'))
        self.assertEqual(7, obj2brain(document).filesize)

        document.file = None
        document.reindexObject()
        self.assertEqual(0, index_data_for(document).get('filesize'))
        self.assertEqual(0, obj2brain(document).filesize)

    def test_filename_indexers(self):
        document = create(
            Builder("document")
            .titled(u'D\xf6k\xfcm\xe4nt')
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(u'Doekuemaent.txt', filename_indexer(document)())
        self.assertEqual(u'Doekuemaent.txt', obj2brain(document).filename)

        document.file = None
        document.reindexObject()
        self.assertEqual(u'', filename_indexer(document)())
        self.assertEqual(u'', obj2brain(document).filename)

    def test_file_extension_indexers(self):
        document = create(
            Builder("document")
            .titled(u'D\xf6k\xfcm\xe4nt')
            .attach_file_containing(u"content", name=u"file.txt")
        )
        document.reindexObject()
        self.assertEqual(u'.txt', index_data_for(document).get('file_extension'))
        self.assertEqual(u'.txt', obj2brain(document).file_extension)

        document.file = None
        document.reindexObject()
        self.assertEqual(u'', index_data_for(document).get('file_extension'))
        self.assertEqual(u'', obj2brain(document).file_extension)

    def test_date_indexers(self):
        creation_date = datetime.datetime(2016, 1, 1, 0, 0, tzinfo=pytz.UTC)
        with freeze(creation_date):
            doc1 = create(Builder('document').having(
                title=u"Doc One",
                document_date=datetime.date(2011, 1, 1),
                receipt_date=datetime.date(2011, 2, 1)))

        # document_date
        self.assertEquals(
            obj2brain(doc1).document_date, datetime.date(2011, 1, 1))

        # receipt_date
        self.assertEquals(
            obj2brain(doc1).receipt_date, datetime.date(2011, 2, 1))

        # delivery_date
        self.assertEquals(
            obj2brain(doc1).delivery_date, None)

        # changed
        self.assertEquals(
            obj2brain(doc1).changed, creation_date)

    def test_checked_out_indexer(self):
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_date=datetime.date(2011, 1, 1),
            receipt_date=datetime.date(2011, 2, 1))

        self.annotations = IAnnotations(doc1)
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = 'TEST_USER_ID'

        doc1.reindexObject()

        self.assertEquals(
            obj2brain(doc1).checked_out, 'TEST_USER_ID')

    def test_external_reference(self):
        doc = create(Builder('document').having(
            author=u'Hugo Boss',
            title=u'Docment',
            foreign_reference=u'qpr-900-9001-\xf8'))

        self.assertEquals(
            u'qpr-900-9001-\xf8',
            index_data_for(doc).get('external_reference'))

    def test_indexer_picks_correct_doc_indexer_adapter_by_default(self):
        sample_file = NamedBlobFile('foo', filename=u'test.txt')
        doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            title=u"Doc One",
            document_author=u'Hugo Boss',
            file=sample_file)

        fulltext_indexer = getAdapter(doc1, IDocumentIndexer)
        self.assertEquals(fulltext_indexer.__class__,
                          DefaultDocumentIndexer)

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        create(Builder("document")
               .having(keywords=(u'Keyword 1', u'Keyword with \xf6')))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

    def test_metadata_contains_reference_number(self):
        doc = create(Builder("document"))
        self.assertEqual(metadata(doc)(), 'Client1 / 1')

    def test_metadata_contains_description(self):
        doc = create(Builder("document").having(description=u'Foo bar baz.'))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Foo bar baz.')

    def test_metadata_contains_keywords(self):
        doc = create(Builder("document").having(keywords=(u'Foo', u'Bar')))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Foo Bar')

    def test_metadata_contains_foreign_reference(self):
        doc = create(Builder("document").having(foreign_reference=u'Ref 123'))
        self.assertEqual(metadata(doc)(), 'Client1 / 1 Ref 123')

    def test_metadata_contains_custom_properties_from_default_and_active_slot(self):
        self.login(TEST_USER_NAME)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"f1", u"Field 1", u"", False)
        )
        create(
            Builder("property_sheet_schema")
            .named("schema2")
            .assigned_to_slots(u"IDocumentMetadata.document_type.report")
            .with_field("text", u"f1", u"Field 1", u"", False)
        )
        doc = create(Builder("document").having(document_type=u"question"))
        IDocumentCustomProperties(doc).custom_properties = {
            "IDocumentMetadata.document_type.question": {"f1": "indexme-question"},
            "IDocumentMetadata.document_type.report": {"f1": "noindex-report"},
            "IDocument.default": {"f1": "indexme-default"},
        }
        self.assertEqual(
            metadata(doc)(),
            'Client1 / 1 indexme-question indexme-default',
        )

    def test_metadata_with_custom_properties_for_all_field_types(self):
        self.login(TEST_USER_NAME)

        choices = ["rot", u"gr\xfcn", "blau"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field("choice", u"choose", u"Choose", u"", True, values=choices)
            .with_field("multiple_choice", u"choosemulti",
                        u"Choose Multi", u"", True, values=choices)
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
            .with_field("date", u"date", u"Date", u"", True)
        )
        doc = create(Builder("document").having(document_type=u"question"))
        IDocumentCustomProperties(doc).custom_properties = {
            "IDocumentMetadata.document_type.question": {
                "yesorno": False,
                "choose": u"gr\xfcn",
                "choosemulti": ["rot", "blau"],
                "num": 122333,
                "text": u"K\xe4fer\nJ\xe4ger",
                "textline": u"Kr\xe4he",
                "date": date(2021, 12, 21)
            },
        }
        indexed_value = metadata(doc)().decode('utf8')
        self.assertIn(u"gr\xfcn", indexed_value)
        self.assertIn(u"122333", indexed_value)
        self.assertIn(u"K\xe4fer", indexed_value)
        self.assertIn(u"J\xe4ger", indexed_value)
        self.assertIn(u"Kr\xe4he", indexed_value)
        self.assertIn(u"rot", indexed_value)
        self.assertIn(u"blau", indexed_value)
        self.assertIn(u"2021-12-21", indexed_value)


class SolrDocumentIndexer(SolrIntegrationTestCase):

    def test_full_text_indexing_with_plain_text(self):
        self.login(self.regular_user)
        self.assertIn('Komentar text',
                      solr_data_for(self.proposaldocument, 'SearchableText'))

    def test_full_text_indexing_with_word_document(self):
        self.login(self.regular_user)
        self.assertIn('Example word document.',
                      solr_data_for(self.document, 'SearchableText'))

    def test_searchable_text(self):
        self.login(self.regular_user)
        document = create(Builder("document").within(self.dossier)
                          .titled(u"Doc One")
                          .having(keywords=(u'foo', 'bar',),
                                  document_author=u'Hugo Boss',
                                  ))
        self.commit_solr()

        indexed_value = solr_data_for(document, 'SearchableText')
        self.assertIn(u'Doc One Hugo Boss Client1 1.1 / 1 / 46 46 foo bar',
                      indexed_value)

    def test_containing_subdossier_is_indexed_for_document_in_subdossiertemplate(self):
        self.login(self.regular_user)
        document = create(Builder("document").within(self.subdossiertemplate))
        self.commit_solr()
        self.assertEqual(u'Anfragen', solr_data_for(document)['containing_subdossier'])

    def test_containing_dossier_is_indexed_for_document_templates(self):
        self.login(self.regular_user)
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.supported_langs = ['fr', 'de-ch']
        self.normal_template.reindexObject()
        self.subtemplate.reindexObject()
        self.commit_solr()

        self.assertEqual(u'Mod\xe8le / Vorlagen',
                         solr_data_for(self.normal_template)['containing_dossier'])
        self.assertEqual(u'Mod\xe8les nouveau / Vorlagen neu',
                         solr_data_for(self.subtemplate)['containing_dossier'])

    def test_removing_document_type_gets_indexed_correctly(self):
        self.login(self.regular_user)
        self.assertEqual('contract', solr_data_for(self.document, 'document_type'))

        self.document.document_type = None
        self.document.reindexObject(idxs=['document_type'])
        self.commit_solr()

        self.assertIsNone(solr_data_for(self.document, 'document_type'))

    def test_document_watchers_are_indexed_in_solr(self):
        self.activate_feature('activity')
        self.login(self.regular_user)

        center = notification_center()
        center.add_watcher_to_resource(
            self.document, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        indexed_value = solr_data_for(self.document, 'watchers')
        self.assertEqual([self.regular_user.getId()], indexed_value)

    def test_mail_watchers_are_indexed_in_solr(self):
        self.activate_feature('activity')
        self.login(self.regular_user)

        center = notification_center()
        center.add_watcher_to_resource(
            self.mail_eml, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        indexed_value = solr_data_for(self.mail_eml, 'watchers')
        self.assertEqual([self.regular_user.getId()], indexed_value)

    def test_approval_state_is_none_if_missing_in_solr(self):
        self.login(self.regular_user)

        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(None, indexed_value)

    def test_approval_state_is_updated_if_approval_added(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)

        # Not approved
        versioner.create_version('Initial version')
        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(None, indexed_value)

        # Approved in current version
        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime.datetime(2021, 7, 2))
        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(APPROVED_IN_CURRENT_VERSION, indexed_value)

    def test_approval_state_is_updated_when_new_version_created(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')
        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime.datetime(2021, 7, 2))

        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(APPROVED_IN_CURRENT_VERSION, indexed_value)

        versioner.create_version('Second version')

        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(APPROVED_IN_OLDER_VERSION, indexed_value)

    def test_approval_state_is_updated_on_revert_to_version(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')

        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(None, indexed_value)

        versioner.create_version('Second version')
        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime.datetime(2021, 7, 2))

        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(APPROVED_IN_CURRENT_VERSION, indexed_value)

        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)

        manager.revert_to_version(0)
        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')

        # Currently we only ensure the approval_state is *updated* on revert.
        # But we might possibly also make sure it's getting *fixed*:
        # Reverting to a version that was previously approved will currently
        # result in a new version that isn't approved yet. If we want to
        # retain that approval, we'd need to copy the approval list when
        # reverting.
        self.assertEqual(APPROVED_IN_OLDER_VERSION, indexed_value)

    def test_approval_state_approved_in_current_version_is_retained_when_document_copied(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)

        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime.datetime(2021, 7, 2))

        copied_doc = api.content.copy(self.document, target=self.subdossier)

        self.commit_solr(avoid_blob_extraction=True)

        indexed_value = solr_data_for(copied_doc, 'approval_state')
        self.assertEqual(APPROVED_IN_CURRENT_VERSION, indexed_value)

    def test_approval_state_approved_in_older_version_is_lost_when_document_copied(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')

        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime.datetime(2021, 7, 2))

        self.commit_solr()

        versioner.create_version('Second version')
        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'approval_state')
        self.assertEqual(APPROVED_IN_OLDER_VERSION, indexed_value)

        copied_doc = api.content.copy(self.document, target=self.subdossier)

        self.commit_solr(avoid_blob_extraction=True)

        indexed_value = solr_data_for(copied_doc, 'approval_state')
        self.assertEqual(None, indexed_value)

    def test_filename_is_updated_on_create_version_and_revert_to_version(self):
        self.login(self.regular_user)

        versioner = Versioner(self.document)
        versioner.create_version('Initial version')

        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'filename')
        self.assertEqual(u'Vertraegsentwurf.docx', indexed_value)

        self.document.file = NamedBlobFile(data='New', filename=u'Vertraegsentwurf.pdf')
        versioner.create_version('Second version')
        self.commit_solr()

        indexed_value = solr_data_for(self.document, 'filename')
        self.assertEqual(u'Vertraegsentwurf.pdf', indexed_value)

        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)

        manager.revert_to_version(0)
        self.commit_solr()
        indexed_value = solr_data_for(self.document, 'filename')

        self.assertEqual(u'Vertraegsentwurf.docx', indexed_value)

    @browsing
    def test_related_items_is_updated_when_forward_relations_are_modified(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual([], self.document.related_items())
        self.assertEqual(None, solr_data_for(self.document, 'related_items'))

        browser.open(self.document, view='edit')
        browser.fill({'Related documents': [self.subdocument.absolute_url_path()]})
        browser.find('Save').click()

        self.commit_solr()
        self.assertEqual([self.subdocument], self.document.related_items())
        self.assertEqual([self.subdocument.UID()],
                         solr_data_for(self.document, 'related_items'))

    @browsing
    def test_related_items_is_updated_when_related_item_is_deleted(self, browser):
        self.login(self.regular_user, browser)
        intids = getUtility(IIntIds)
        IRelatedDocuments(self.document).relatedItems = [
            RelationValue(intids.getId(self.subdocument))]
        update_behavior_relations(self.document, None)
        self.document.reindexObject(idxs=["related_items"])
        self.commit_solr()

        self.assertEqual(
            [self.subdocument],
            [rel.to_object for rel in IRelatedDocuments(self.document).relatedItems])
        self.assertEqual([self.subdocument.UID()],
                         solr_data_for(self.document, 'related_items'))

        with self.login(self.manager):
            api.content.delete(self.subdocument)

        self.commit_solr()
        # Relations do not get deleted, only broken
        relations = IRelatedDocuments(self.document).relatedItems
        self.assertEqual(1, len(relations))
        self.assertTrue(relations[0].isBroken())
        # Index should only contain unbroken relations
        self.assertEqual(None, solr_data_for(self.document, 'related_items'))

    def test_document_version_count_indexed(self):
        self.login(self.regular_user)
        versioner = Versioner(self.document)
        versioner.create_version('Initial version')
        versioner.create_version('Second version')
        self.commit_solr()

        indexed_value = solr_data_for(self.document, 'document_version_count')
        self.assertEqual(indexed_value, 2)
        self.assertEqual(indexed_value, self.document.get_current_version_id() + 1)

    def test_mail_version_count_indexed(self):
        """mails are read only (no Edit) therefor the version should never changes
        """
        self.login(self.regular_user)

        # version a mail should not affect its version ID
        versioner = Versioner(self.mail_eml)
        versioner.create_version('Initial version')
        versioner.create_version('Second version')

        self.commit_solr()
        indexed_value = solr_data_for(self.mail_eml, 'document_version_count')

        # Explicit assertion to confirm indexing matches method return value
        self.assertEqual(indexed_value, self.mail_eml.get_current_version_id() + 1)

        # Mails are always on version 0
        self.assertEqual(indexed_value, 1)
