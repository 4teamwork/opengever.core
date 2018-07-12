from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.locking.interfaces import IRefreshableLockable
from zExceptions import Unauthorized


class TestDocumentQuickupload(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentQuickupload, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .titled('Anfrage Herr Meier')
                               .checked_out()
                               .attach_file_containing('OLD DATA')
                               .within(self.dossier))

    def test_raises_unauthorized_when_document_is_not_checked_out(self):
        document = create(Builder('document'))
        with self.assertRaises(Unauthorized):
            create(Builder('quickuploaded_document')
                   .within(document)
                   .with_data('text'))

    def test_raises_unauthorized_when_document_is_locked(self):
        IRefreshableLockable(self.document).lock()

        with self.assertRaises(Unauthorized):
            create(Builder('quickuploaded_document')
                   .within(self.document)
                   .with_data('text'))

    def test_file_is_updated(self):
        create(Builder('quickuploaded_document')
               .within(self.document)
               .with_data('NEW DATA'))

        self.assertEquals('NEW DATA', self.document.file.data)

    def test_uses_existing_filename_but_new_extension(self):
        create(Builder('quickuploaded_document')
               .within(self.document)
               .with_data('NEW DATA', filename='test.pdf'))

        self.assertEquals('Anfrage Herr Meier.pdf',
                          self.document.file.filename)
