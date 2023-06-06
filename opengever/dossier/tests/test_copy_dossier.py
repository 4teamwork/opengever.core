from ftw.builder import Builder
from ftw.builder import create
from OFS.interfaces import IObjectWillBeRemovedEvent
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestCopyDossiers(SolrIntegrationTestCase):

    def test_copying_dossier_purges_child_reference_number_mappings(self):
        self.login(self.dossier_responsible)
        subdossier = create(Builder('dossier').within(self.empty_dossier))

        dossier_copy = api.content.copy(
            source=self.empty_dossier, target=self.empty_repofolder)

        # subdossier is copied
        self.assertEqual(1, len(dossier_copy.get_subdossiers()))
        subdossier_copy = dossier_copy.get_subdossiers()[0].getObject()

        # copied dossier contains mappings for copied subdossiers starting at
        # 1, the mapping was purged on copy
        ref = IReferenceNumberPrefix(dossier_copy)
        self.assertItemsEqual(
            [u'1'],
            ref.get_child_mapping(subdossier_copy).keys())

        # there are no more entries for the previous subdossiers
        intids = getUtility(IIntIds)
        prefixed_intids = ref.get_prefix_mapping(subdossier_copy).keys()
        self.assertNotIn(intids.getId(subdossier), prefixed_intids)
        self.assertIn(intids.getId(subdossier_copy), prefixed_intids)

    def test_indexes_are_updated_when_dossier_is_copied(self):
        self.login(self.dossier_responsible)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdossier)
        self.assert_solr_field_value(1, 'is_subdossier', self.subdossier)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subsubdossier)
        self.assert_solr_field_value(1, 'is_subdossier', self.subsubdossier)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdocument)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', self.subdocument)

        dossier_copy = api.content.copy(
            source=self.subdossier, target=self.leaf_repofolder)

        self.commit_solr(avoid_blob_extraction=True)

        subdossier_copy = api.content.find(
            context=dossier_copy, portal_type='opengever.dossier.businesscasedossier',
            depth=1)[0].getObject()

        subdocument_copy = api.content.find(
            context=dossier_copy, portal_type='opengever.document.document',
            depth=1)[0].getObject()

        self.assert_solr_field_value(dossier_copy.Title(),
                                     'containing_dossier', dossier_copy)
        self.assert_solr_field_value(0, 'is_subdossier', dossier_copy)

        self.assert_solr_field_value(dossier_copy.Title(),
                                     'containing_dossier', subdossier_copy)
        self.assert_solr_field_value(1, 'is_subdossier', subdossier_copy)

        self.assert_solr_field_value(dossier_copy.Title(),
                                     'containing_dossier', subdocument_copy)
        self.assert_solr_field_value('', 'containing_subdossier',
                                     subdocument_copy)

    def test_copying_tasks_is_prevented(self):
        self.login(self.dossier_responsible)

        create(Builder('task')
               .within(self.empty_dossier)
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId()))

        register_event_recorder(IObjectWillBeRemovedEvent)

        copied_dossier = api.content.copy(
            source=self.empty_dossier, target=self.empty_repofolder)
        self.assertItemsEqual([], copied_dossier.getFolderContents())

        self.assertFalse(
            any(IObjectWillBeRemovedEvent.providedBy(event) for
                event in get_recorded_events())
        )
