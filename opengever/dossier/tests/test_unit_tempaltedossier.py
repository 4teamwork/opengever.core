from Products.CMFCore.interfaces import ISiteRoot
from datetime import datetime
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.base.interfaces import IRedirector
from opengever.document import document
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IDocumentSettings
from opengever.dossier.templatedossier import ITemplateUtility
from opengever.dossier.templatedossier import TemplateDocumentFormView
from plone.dexterity.fti import DexterityFTI, register
from plone.registry.interfaces import IRegistry
from plone.rfc822.interfaces import IPrimaryField
from zope.component import getGlobalSiteManager
from zope.component import getUtility, provideAdapter
from zope.component import provideUtility
from zope.component.persistentregistry import PersistentComponents
from zope.container.interfaces import INameChooser
from zope.interface import Interface, implements, alsoProvides
from z3c.blobfile import storages, interfaces


class TestTemplateFolderUtility(MockTestCase):

    def setUp(self):
        grok('opengever.dossier.templatedossier')

    def test_templatefolder_returns_path(self):
        brain = self.mocker.mock()
        self.expect(brain.getPath()).result('plone/test')

        mock_catalog = self.mocker.mock()
        self.mock_tool(mock_catalog, 'portal_catalog')
        self.expect(mock_catalog(
                portal_type="opengever.dossier.templatedossier")
                    ).result([brain, ])

        self.replay()

        templateUtil = getUtility(
            ITemplateUtility, 'opengever.templatedossier')

        self.assertEqual(templateUtil.templateFolder(object()), 'plone/test')

    def test_templatefolder_returns_none_without_templatedossier(self):
        mock_catalog = self.mocker.mock()
        self.mock_tool(mock_catalog, 'portal_catalog')
        self.expect(mock_catalog(
                portal_type="opengever.dossier.templatedossier")
                    ).result([])

        self.replay()

        templateUtil = getUtility(
            ITemplateUtility, 'opengever.templatedossier')

        self.assertEqual(templateUtil.templateFolder(object()), None)


def registerUtilities():
     provideUtility(storages.StringStorable(),
                                   interfaces.IStorage,
                                   name="__builtin__.str")
     provideUtility(storages.UnicodeStorable(),
                                   interfaces.IStorage,
                                   name="__builtin__.unicode")
     provideUtility(storages.FileChunkStorable(),
                                   interfaces.IStorage,
                                   name="zope.app.file.file.FileChunk")
     provideUtility(storages.FileDescriptorStorable(),
                                   interfaces.IStorage,
                                   name="__builtin__.file")


class TestTemplateDocumentFormView(MockTestCase):

    def setUp(self):
        super(TestTemplateDocumentFormView, self).setUp()
        grok('opengever.dossier.templatedossier')
        registerUtilities()

    def test_activating_external_editing(self):
        mock_context = self.mocker.mock()
        manager = self.mocker.mock()
        self.expect(manager.checkout(mock_context)).result(None)
        self.expect(
            mock_context.restrictedTraverse('checkout_documents')).result(
            manager)

        self.expect(mock_context.absolute_url()).result('http://foo.com')
        mock_request = self.mocker.mock(count=False)

        redirector = self.mocker.mock()
        self.expect(redirector(mock_request)).result(redirector)
        self.expect(redirector.redirect(
            'http://foo.com/external_edit',
            target="_self",
            timeout=1000)).result(None)

        self.mock_adapter(redirector, IRedirector, [Interface, ])

        self.replay()

        view = TemplateDocumentFormView(mock_context, mock_request)
        view.activate_external_editing(mock_context)

    def _mock_context_and_request(self):
        #mocking context and request
        mock_context = self.mocker.mock()
        mock_response = self.mocker.mock()
        self.expect(mock_context.absolute_url()).result(
            'http://foo.com').count(0, None)
        mock_request = self.mocker.mock(count=False)
        self.expect(mock_request.RESPONSE).result(
            mock_response).count(0, None)
        return mock_context, mock_request, mock_response

    def test_call_view_first_time(self):
        mock_context, mock_request, mock_response = self._mock_context_and_request()
        self.expect(mock_request.get('form.buttons.save')).result(False)
        self.expect(mock_request.get('form.buttons.cancel')).result(False)

        view = TemplateDocumentFormView(mock_context, mock_request)
        mock_view = self.mocker.patch(view)
        self.expect(mock_view.render_form()).result('test-render-form')
        self.replay()
        self.assertEqual(mock_view(), 'test-render-form')

    def test_call_view_cancel_button(self):
        mock_context, mock_request, mock_response = self._mock_context_and_request()
        self.expect(
            mock_request.get('form.buttons.save')).result(False)
        self.expect(
            mock_request.get('form.buttons.cancel')).result('True')
        #expect redirecting
        self.expect(mock_response.redirect('http://foo.com'))
        self.replay()

        view = TemplateDocumentFormView(mock_context, mock_request)
        view()

    def test_saving_form_without_selecting_template(self):
        mock_context, mock_request, mock_response = self._mock_context_and_request()
        self.expect(mock_request.get('form.buttons.save')).result(True)
        self.expect(mock_request.get('title', '')).result('Test Title')
        self.expect(mock_request.get('paths')).result(False)
        self.expect(
            mock_request.get('form.widgets.edit_form')).result(None)

        #expect redirecting
        view = TemplateDocumentFormView(mock_context, mock_request)
        mock_view = self.mocker.patch(view)
        self.expect(mock_view.render_form()).result('test-render-form')
        self.replay()
        self.assertEqual(mock_view(), 'test-render-form')

    def test_saving_form(self):
        mock_context, mock_request, mock_response = self._mock_context_and_request()
        self.expect(mock_request.get('form.buttons.save')).result(True)
        self.expect(mock_request.get('title', '')).result('Test Title')
        self.expect(mock_request.get('paths')).result(
            ['plone/testpath/', ]).count(0, None)
        self.expect(
            mock_request.get('form.widgets.edit_form')).result(['on'])

        view = TemplateDocumentFormView(mock_context, mock_request)
        mock_view = self.mocker.patch(view)
        self.expect(mock_view.create_document('plone/testpath/')).result(
            'new-document')
        self.expect(mock_view.activate_external_editing('new-document'))

        mock_response.redirect('http://foo.com#documents')
        self.replay()
        mock_view()

    def test_create_document_method(self):

        # we need to register any plone.directives.form magic components
        # from the module manually (they are not grokky):
        for factory, name in document.__form_value_adapters__:
            provideAdapter(factory, name=name)

        class MockContext(object):
            def __init__(self, fti, template):
                self.fti = fti
                self.template = template
            def _setObject(self, id, obj):
                self.obj = obj
            def _getOb(self, id):
                return self.obj
            def restrictedTraverse(self, testpath):
                return self.template
            def getTypeInfo(self):
                return self.fti

        # Mock the lookup of the site and the site manager at the site root
        dummy_site = self.create_dummy()
        self.mock_utility(dummy_site, ISiteRoot)

        # fti fake
        fti = DexterityFTI(u'opengever.document.document')
        fti.schema = 'opengever.document.document.IDocumentSchema'
        fti.model_source = None
        fti.model_file = None
        fti.addable_types = ['opengever.document.document']
        fti.isConstructionAllowed = lambda x: True
        fti.allowType = lambda x: True
        register(fti)
        site_manager_mock = self.mocker.proxy(
            PersistentComponents(bases=(getGlobalSiteManager(),)))
        getSiteManager_mock = self.mocker.replace(
            'zope.app.component.hooks.getSiteManager')
        self.expect(
            getSiteManager_mock(
                dummy_site)).result(site_manager_mock).count(0 , None)

        alsoProvides(IDocumentSchema.get('file'), IPrimaryField)

        # Name chooser
        class NameChooser(object):
            implements(INameChooser)
            def __init__(self, context):
                pass
            def chooseName(self, name, object):
                return u"newid"
        self.mock_adapter(NameChooser, INameChooser, (Interface,))

        # template
        namedfile = self.stub()
        template_doc = self.stub()
        self.expect(template_doc.file).result(namedfile)
        self.expect(template_doc.portal_type).result(
            'opengever.document.document')
        self.expect(namedfile.data).result('data data data')
        self.expect(namedfile.filename).result(u'test_filename.doc')

        # context and request
        context = MockContext(fti, template_doc)
        request = self.stub_request()
        testpath = 'testpath'

        # registry
        registry_mock = self.stub()
        self.expect(registry_mock.forInterface(IDocumentSettings)).result(registry_mock)
        self.expect(registry_mock.preserved_as_paper_default).result(False)
        self.mock_utility(registry_mock, IRegistry)

        self.replay()
        view = TemplateDocumentFormView(context, request)
        view.title = u'Test Title'

        view.create_document(testpath)

        self.assertEqual(context.obj.portal_type, u'opengever.document.document')
        self.assertFalse(context.obj.file == namedfile)
        self.assertEquals(context.obj.file.data, namedfile.data)
        self.assertEqual(context.obj.document_date, datetime.now().date())
        self.assertEqual(context.obj.preserved_as_paper, False)
