from mocker import ANY, IN
from OFS.CopySupport import CopyError
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.move_items import MoveItemsForm
from plone.mocktestcase import MockTestCase
from Products.statusmessages.interfaces import IStatusMessage
from webdav.Lockable import ResourceLockedError
from zope.interface import Interface, directlyProvides


class TestOpengeverDossierMoveItems(MockTestCase):


    def test_handle_submit(self):
        """ Test handle_submit method from MoveItemsForm class
        """
        # Parent-Object-Task
        mock_parent_task = self.create_dummy()

        # Source-Object in Task
        src_task = self.create_dummy()
        directlyProvides(src_task, IDocumentSchema)
        mock_src_task = self.mocker.proxy(src_task, spec=False, count=False)
        self.expect(mock_src_task.__parent__).result(mock_parent_task)
        self.expect(mock_src_task.title).result('doc_in_task')
        self.expect(mock_src_task.id).result('doc_in_task')

        # Parent-Object-Dossier
        parent = self.create_dummy()
        directlyProvides(parent, IDossierMarker)
        mock_parent_dossier = self.mocker.proxy(parent, spec=None, count=False)
        self.expect(
            mock_parent_dossier.manage_cutObjects(
                IN(['normal', 'copy', 'value', ]))).call(lambda a: a)
        self.expect(
            mock_parent_dossier.manage_cutObjects(
                'webdav')).throw(ResourceLockedError)

        # Source-Object normal (without a error)
        mock_src_normal = self.mocker.mock(count=False)
        self.expect(mock_src_normal.__parent__).result(mock_parent_dossier)
        self.expect(
            mock_src_normal.portal_type).result('opengever.document.document')
        self.expect(mock_src_normal.title).result('normal_doc')
        self.expect(mock_src_normal.id).result('normal')

        # Source-Object locked via webdav
        mock_src_webdav = self.mocker.mock(count=False)
        self.expect(mock_src_webdav.__parent__).result(mock_parent_dossier)
        self.expect(
            mock_src_webdav.portal_type).result('opengever.document.document')
        self.expect(mock_src_webdav.title).result('webdav_doc')
        self.expect(mock_src_webdav.id).result('webdav')

        # Source-Object value error
        mock_src_value = self.mocker.mock(count=False)
        self.expect(mock_src_value.__parent__).result(mock_parent_dossier)
        self.expect(
            mock_src_value.portal_type).result('opengever.document.document')
        self.expect(mock_src_value.title).result('value_doc')
        self.expect(mock_src_value.id).result('value')

        # Source-Object copy error
        mock_src_copy = self.mocker.mock(count=False)
        self.expect(mock_src_copy.__parent__).result(mock_parent_dossier)
        self.expect(
            mock_src_copy.portal_type).result('opengever.document.document')
        self.expect(mock_src_copy.title).result('copy_doc')
        self.expect(mock_src_copy.id).result('copy')

        # Context
        mock_context = self.mocker.mock(count=False)
        self.expect(
            mock_context.unrestrictedTraverse(
                '/doc_in_task')).result(mock_src_task)
        self.expect(
            mock_context.unrestrictedTraverse(
                '/webdav')).result(mock_src_webdav)
        self.expect(
            mock_context.unrestrictedTraverse(
                '/normal')).result(mock_src_normal)
        self.expect(
            mock_context.unrestrictedTraverse(
                '/value')).result(mock_src_value)
        self.expect(
            mock_context.unrestrictedTraverse(
                '/copy')).result(mock_src_copy)

        # Statusmessage
        class Statusmessage(object):

            msg = []
            msg_type = []

            def __call__(self, request):
                return self

            def addStatusMessage(self, msg, type):
                self.msg.append(msg)
                self.msg_type.append(type)

        sm = Statusmessage()
        self.mock_adapter(sm, IStatusMessage, [Interface])

        # Request
        request = self.create_dummy()
        mock_request = self.mocker.proxy(request)
        self.expect(mock_request.RESPONSE.redirect(ANY)).result('redirect')

        # Destination
        mock_destination = self.mocker.mock(count=False)
        self.expect(mock_destination.absolute_url()).result('/plone/dest/')
        self.expect(
            mock_destination.manage_pasteObjects(
                'value')).throw(ValueError).count(0, None)
        self.expect(
            mock_destination.manage_pasteObjects(
                'copy')).throw(CopyError).count(0, None)
        self.expect(
            mock_destination.manage_pasteObjects(
                'normal')).result('True').count(0, None)

        # Mocked data from the webform
        data = {
            'destination_folder': mock_destination,
            'request_paths': u'/doc_in_task;;' \
                              '/webdav;;' \
                              '/value;;' \
                              '/copy;;' \
                              '/normal'}

        # MoveItems Class
        move_items = MoveItemsForm(mock_context, mock_request)
        mock_move_items = self.mocker.proxy(move_items, spec=None)
        self.expect(mock_move_items.extractData()).result([data,[]])

        self.replay()

        mock_move_items.handle_submit(mock_move_items, 'action')

        # Check
        self.assertIn('Please move the Task', sm.msg[0])
        self.assertIn("error", sm.msg_type[0])

        self.assertIn('Elements were moved successfully', sm.msg[1])
        self.assertIn("info", sm.msg_type[1])

        self.assertIn('Failed to copy following objects', sm.msg[2])
        self.assertIn("error", sm.msg_type[2])

        self.assertIn('Locked via WebDAV', sm.msg[3])
        self.assertIn("error", sm.msg_type[3])
