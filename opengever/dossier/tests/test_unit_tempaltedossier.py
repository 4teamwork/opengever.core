from grokcore.component.testing import grok
from mocker import ANY
from opengever.base.interfaces import IRedirector
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.templatedossier import ITemplateUtility
from opengever.dossier.templatedossier import TemplateDocumentFormView
from plone.mocktestcase import MockTestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent


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


class TestTemplateDocumentFormView(MockTestCase):

    def setUp(self):
        grok('opengever.dossier.templatedossier')

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
        """Test the create_document method,
        which copies the template and adjust the copy"""

        mock_context = self.mocker.mock()
        mock_request = self.mocker.mock(count=False)
        template_doc = self.mocker.mock()
        newdoc = self.mocker.mock()

        # mock the copy process
        self.expect(template_doc.__parent__).result(template_doc)
        self.expect(template_doc.getId()).result('test-id')
        self.expect(
            template_doc.manage_copyObjects(['test-id'])).result('clipboard')
        self.expect(mock_context.manage_pasteObjects('clipboard')).result(
            [{'new_id': 'new-id'}, ])
        self.expect(mock_context.get('new-id')).result(newdoc)

        #portal_membership
        mtool = self.mocker.mock()
        member = self.mocker.mock()
        self.expect(member.title_or_id()).result('test-user-id')
        self.expect(member.getId()).result('test-user-id')
        self.expect(mtool.getAuthenticatedMember()).result(member)
        self.mock_tool(mtool, 'portal_membership')

        # mock the newdoc object
        self.expect(newdoc.getId()).result('new-id').count(2)
        self.expect(newdoc.setTitle('Test Title'))
        newdoc.creators = ('test-user-id',)
        newdoc.changeOwnership(member)
        newdoc.creation_date = ANY
        newdoc.document_date = None
        newdoc.document_author = None
        self.expect(
            newdoc.get_local_roles()).result((('admin', ('Owner', 'Editor')),))
        newdoc.manage_delLocalRoles(['admin'])
        newdoc.manage_setLocalRoles('test-user-id', ('Owner',))

        # mock events
        self.expect(ObjectModifiedEvent(newdoc)).result('mockevent')
        notify('mockevent')

        #mock annotation
        ann_adapter = self.mocker.mock()
        self.expect(ann_adapter(newdoc)).result(ann_adapter)
        self.expect(ann_adapter.keys()).result(['test-key'])
        del ann_adapter['test-key']
        # self.expect(ann_adapter.keys()).result([])
        self.mock_adapter(ann_adapter, IAnnotations, [Interface, ])

        # ISequence_number utility
        sequence_number_utility = self.mocker.mock()
        self.expect(sequence_number_utility.get_number(newdoc)).result('10')
        self.mock_utility(sequence_number_utility, ISequenceNumber)

        testpath = '/plone/testpath'

        # mock context methods
        self.expect(mock_context.absolute_url()).result(
            'http://foo.com').count(0, None)
        self.expect(mock_context.restrictedTraverse(testpath)).result(
            template_doc)
        mock_context.manage_renameObject('new-id', 'document-10')

        self.replay()

        view = TemplateDocumentFormView(mock_context, mock_request)
        view.title = 'Test Title'

        newdoc = view.create_document(testpath)
