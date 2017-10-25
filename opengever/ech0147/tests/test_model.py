from opengever.ech0147.model import Directive
from opengever.ech0147.model import Document
from opengever.ech0147.model import Dossier
from opengever.ech0147.model import MessageT1
from opengever.testing import IntegrationTestCase
from plone import api

import unittest


class DummyZipFile(object):
    def __init__(self):
        self.filenames = []
        self.arcnames = []

    def write(self, filename, arcname):
        self.filenames.append(filename)
        self.arcnames.append(arcname)


class TestMessageModel(IntegrationTestCase):

    def setUp(self):
        super(TestMessageModel, self).setUp()
        self.login(self.administrator)

    def test_binding_of_empty_message_is_valid(self):
        msg = MessageT1()
        self.assertTrue(msg.binding().validateBinding())

    def test_senderid_defaults_to_current_users_email(self):
        member = api.user.get_current()
        member.setProperties({'email': 'foo@bar.net'})
        msg = MessageT1()
        header = msg.header()
        self.assertEqual(u'foo@bar.net', header.senderId)

    def test_sending_application_and_version(self):
        msg = MessageT1()
        header = msg.header()
        self.assertEqual(
            u'4teamwork AG', header.sendingApplication.manufacturer)
        self.assertEqual(
            u'OneGov GEVER', header.sendingApplication.product)
        self.assertRegexpMatches(
            header.sendingApplication.productVersion,
            r'\d{4}\.\d+\.\d',
            msg="Doesn't look like a version number")

    def test_adding_a_document(self):
        msg = MessageT1()
        msg.add_object(self.document)
        self.assertEqual(1, len(msg.documents))
        self.assertEqual(self.document, msg.documents[0].obj)
        self.assertTrue(msg.binding().validateBinding())

    def test_adding_a_dossier(self):
        msg = MessageT1()
        msg.add_object(self.dossier)
        self.assertEqual(1, len(msg.dossiers))
        self.assertEqual(self.dossier, msg.dossiers[0].obj)
        self.assertTrue(msg.binding().validateBinding())

    def test_adding_to_zip(self):
        msg = MessageT1()
        msg.add_object(self.dossier)
        msg.add_object(self.document)
        zipfile = DummyZipFile()
        msg.add_to_zip(zipfile)
        self.assertEqual(
            [u'files/dossier-1/dossier-2/ubersicht-der-vertrage-von-2016.xlsx',
             u'files/dossier-1/vertragsentwurf.docx',
             u'files/dossier-1/die-burgschaft.eml',
             u'files/dossier-1/testm\xe4il.msg',
             u'files/dossier-1/initialvertrag-fur-bearbeitung-8-sitzung-der.docx',  # noqa
             u'files/vertragsentwurf.docx'],
            zipfile.arcnames)

    def test_message_with_subjects(self):
        msg = MessageT1()
        msg.subjects = [u'A Subject']
        self.assertTrue(msg.binding().validateBinding())
        header = msg.header()
        self.assertEqual(u'A Subject', header.subjects.subject[0].value())

    def test_message_with_comments(self):
        msg = MessageT1()
        msg.comments = [u'A comment']
        self.assertTrue(msg.binding().validateBinding())
        header = msg.header()
        self.assertEqual(u'A comment', header.comments.comment[0].value())


class TestDossierModel(IntegrationTestCase):

    def setUp(self):
        super(TestDossierModel, self).setUp()
        self.login(self.administrator)

    def test_dossier_binding_is_valid(self):
        dossier = Dossier(self.dossier, u'files')
        self.assertTrue(dossier.binding().validateBinding())

    def test_dossier_path_consists_of_base_path_and_dossier_id(self):
        base_path = u'myfiles/folder'
        dossier = Dossier(self.dossier, base_path)
        self.assertEqual(
            base_path + '/' + self.dossier.getId(), dossier.path)

    def test_dossier_contains_documents_and_mails(self):
        documentish_types = ['opengever.document.document', 'ftw.mail.mail']
        dossier = Dossier(self.dossier, u'files')
        self.assertItemsEqual(
            [d for d in self.dossier.objectValues()
             if d.portal_type in documentish_types],
            [d.obj for d in dossier.documents])

    def test_documents_without_a_file_are_skipped(self):
        self.document.file = None
        dossier = Dossier(self.dossier, u'files')

        self.assertNotIn(self.document, [d.obj for d in dossier.documents])

    def test_dossier_contains_subdossiers(self):
        dossier = Dossier(self.dossier, u'files')
        self.assertItemsEqual(
            [d.getId() for d in self.dossier.objectValues()
                if d.portal_type == 'opengever.dossier.businesscasedossier'],
            [d.obj.getId() for d in dossier.dossiers])


class TestDocumentModel(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentModel, self).setUp()
        self.login(self.administrator)

    def test_document_binding_is_valid(self):
        doc = Document(self.document, u'files')
        self.assertTrue(doc.binding().validateBinding())

    def test_document_path_consists_of_base_path_and_filename(self):
        base_path = u'myfiles/folder'
        doc = Document(self.document, base_path)
        self.assertEqual(
            base_path + '/' + self.document.file.filename, doc.path)


class TestDirectiveModel(unittest.TestCase):

    def test_directive_binding_is_valid(self):
        directive = Directive(u'process')
        self.assertTrue(directive.binding().validateBinding())
