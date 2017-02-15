from opengever.dossier.upgrades.to4502 import drop_old_refnumber_from_annotations
from opengever.testing import FunctionalTestCase
from zope.annotation.interfaces import IAnnotations


class TestDropTemplateFolderReferenceNumber(FunctionalTestCase):

    def setUp(self):
        super(TestDropTemplateFolderReferenceNumber, self).setUp()
        annotations = IAnnotations(self.portal)
        annotations['dossier_reference_mapping'] = 'Foo'
        annotations['reference_numbers'] = 'Bar'
        annotations['reference_prefix'] = 'Qux'

    def test_drop_refnumbers_from_annotations(self):
        drop_old_refnumber_from_annotations()

        annotations = IAnnotations(self.portal)
        self.assertNotIn('dossier_reference_mapping', annotations)
        self.assertNotIn('reference_numbers', annotations)
        self.assertNotIn('reference_prefix', annotations)
