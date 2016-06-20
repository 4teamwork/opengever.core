from ftw.builder import Builder
from ftw.builder import create
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_API_TESTING
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
import transaction
import unittest


class TestContentCreation(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_API_TESTING

    def setUp(self):
        super(TestContentCreation, self).setUp()
        self.portal = self.layer['portal']

        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.repo = create(Builder('repository_root')
                           .having(id='ordnungssystem',
                                   title_de=u'Ordnungssystem',
                                   title_fr=u'Syst\xe8me de classement'))
        self.repofolder = create(Builder('repository')
                                 .within(self.repo)
                                 .having(title_de=u'Ordnungsposition',
                                         title_fr=u'Position'))
        self.dossier = create(Builder('dossier')
                              .within(self.repofolder)
                              .titled(u'Mein Dossier'))

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']
        transaction.commit()

    @unittest.skip("""This test fails because of a broken default value
    lookup for the `privacy_layer` and `classification` fields after patching
    DexterityContent.__getattr__:

    Before the patch, the respective field wasn't even found because
    DexterityContent.__getattr__ looked for it in *marker interfaces* instead
    of schema interfaces. Because the field was never found, __getattr__ did
    raise an AttributeError in the end, and triggered Acquisition. Using
    acquisition, the attribute was looked up on parents (dossiers, repofolders)
    which *did* have a value set, and that's why this ever worked at all.

    With the patch, DexterityContent.__getattr__ now correctly takes schema
    interfaces for behaviors into consideration when looking for the field.
    The field is therefore found. But the `privacy_layer` and `classification`
    fields currently do not have a Field.default(Factory) yet, but still use
    z3c.form default value adapters. The way zope.schema's DefaultProperty is
    implemented though, it always returns a value, `None` if no default is
    set. This doesn't validate, and leads to errors during content creation if
    those fields are omitted.

    Once the default value adapters for those (and possibly other) fields
    have been rewritten as defaultFactories, it should be possible to re-enable
    this test without any changes.
    """)
    def test_dossier_creation(self):
        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'responsible': TEST_USER_ID,
            u'custody_period': 30,
            u'archival_value': u'unchecked',
            u'retention_period': 5,
        }
        response = self.api.post(
            '/ordnungssystem/ordnungsposition', json=payload)
        transaction.commit()

        self.assertEqual(201, response.status_code)

        dossier = self.repofolder.restrictedTraverse('dossier-2')
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', dossier.title)

    @unittest.skip("""This test is failing for the same reason as
    test_dossier_creation above""")
    def test_document_creation(self):
        payload = {
            u'@type': u'opengever.document.document',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'file': {
                u'data': u'TG9yZW0gSXBzdW0uCg==',
                u'encoding': u'base64',
                u'filename': u'b\xe4rengraben.txt',
                u'content-type': u'text/plain'},
        }
        response = self.api.post(
            '/ordnungssystem/ordnungsposition/dossier-1', json=payload)
        transaction.commit()

        self.assertEqual(201, response.status_code)

        doc = self.dossier.restrictedTraverse('document-1')
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', doc.title)
        self.assertEqual(u'sanierung-barengraben-2016.txt', doc.file.filename)
