from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import ISequenceNumber
from opengever.base.interfaces import ISequenceNumberGenerator
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getUtility


class TestSequenceBehavior(IntegrationTestCase):
    """The sequence behavior is tested with the dossier FTI,
    but is used in other types as well.
    """

    def test_sequence_behavior(self):
        self.login(self.regular_user)

        generator = ISequenceNumberGenerator(self.dossier)
        current_number = generator.get_next(generator.key)

        dossier_a = create(Builder('dossier').within(self.leaf_repofolder))
        dossier_b = create(Builder('dossier').within(self.leaf_repofolder))

        sequence_utility = getUtility(ISequenceNumber)
        self.assertEquals(current_number + 1, sequence_utility.get_number(dossier_a))
        self.assertEquals(current_number + 2, sequence_utility.get_number(dossier_b))

    def test_copy_becomes_a_new_number(self):
        self.login(self.regular_user)

        sequence_utility = getUtility(ISequenceNumber)
        generator = ISequenceNumberGenerator(self.dossier)
        current_number = generator.get_next(generator.key)

        dossier_copy = api.content.copy(source=self.empty_dossier,
                                        target=self.leaf_repofolder)

        self.assertEquals(current_number + 1,
                          sequence_utility.get_number(dossier_copy))

    def test_numbering_is_per_type(self):
        self.login(self.regular_user)

        dossier_generator = ISequenceNumberGenerator(self.dossier)
        document_generator = ISequenceNumberGenerator(self.document)

        self.assertNotEqual(dossier_generator.key, document_generator.key)
        self.assertNotEqual(
            dossier_generator.get_next(dossier_generator.key),
            document_generator.get_next(document_generator.key))
