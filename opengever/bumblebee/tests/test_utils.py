from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from opengever.bumblebee import get_representation_url_by_brain
from opengever.bumblebee import get_representation_url_by_object
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone import api


class TestIsBumblebeeFeatureEnabled(FunctionalTestCase):

    def test_true_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IGeverBumblebeeSettings)

        self.assertTrue(is_bumblebee_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IGeverBumblebeeSettings)

        self.assertFalse(is_bumblebee_feature_enabled())


class TestGetRepresentationUrlByObject(FunctionalTestCase):

    def test_returns_representation_url_if_checksum_is_available(self):
        document = create(Builder('document')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        self.assertIn(
            '/YnVtYmxlYmVl/api/v2/resource/',
            get_representation_url_by_object('thumbnail', document))

    def test_returns_preserved_as_paper_placeholder_image_if_no_ckecksum_is_available(self):
        document = create(Builder('document'))

        self.assertIn(
            'preserved_as_paper.png',
            get_representation_url_by_object('thumbnail', document))


class TestGetRepresentationUrlByBrain(FunctionalTestCase):

    def test_returns_representation_url_if_checksum_is_available(self):
        document = create(Builder('document')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))

        brain = obj2brain(document)

        self.assertIn(
            '/YnVtYmxlYmVl/api/v2/resource/',
            get_representation_url_by_brain('thumbnail', brain))

    def test_returns_preserved_as_paper_placeholder_image_if_no_ckecksum_is_available(self):
        document = create(Builder('document'))

        brain = obj2brain(document)

        self.assertIn(
            'preserved_as_paper.png',
            get_representation_url_by_brain('thumbnail', brain))
