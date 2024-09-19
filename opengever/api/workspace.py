from ftw.mail.interfaces import IEmailAddress
from ftw.mail.mail import IMail
from opengever.api.add import GeverFolderPost
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.document.document import IDocumentSchema
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.participation import can_manage_member
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
import json


@implementer(ISerializeToJson)
@adapter(IWorkspace, Interface)
class SerializeWorkspaceToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeWorkspaceToJson, self).__call__(*args, **kwargs)

        result[u"can_manage_participants"] = can_manage_member(self.context)
        result[u"can_access_members"] = self.context.access_members_allowed()
        result[u'email'] = IEmailAddress(self.request).get_email_for_object(self.context)

        return result


class UploadDocumentCopy(GeverFolderPost):
    """Endpoint to upload a complete copy of a GEVER document to a workspace
    or workspace folder.

    Expects a multipart request that includes the document blob as well as
    the document metadata.

    The multipart request must contain a multipart file upload part, as well
    as a second, form encoded part with a `document_metadata` field.

    The value in the form field `document_metadata` is expected to be a
    JSON encoded string with the document's metadata fields in the
    ISerializeToJson serialization format.

    The `gever_document_uid` is the UID of the GEVER document this copy will
    be linked to.
    """

    def extract_data(self):
        data = json.loads(self.request.form['document_metadata'])

        self.type_ = data.get("@type", None)
        self.title_ = data.get("title", None)
        self.gever_document_uid = self.request.form['gever_document_uid']
        self.id_ = None

        if not self.type_:
            raise BadRequest("Property '@type' is required")

        self.file_upload = self.request.form['file']
        self.filename = self.file_upload.filename.decode('utf-8')
        self.content_type = self.file_upload.headers.get('Content-Type')

        # GeverFolderPost will invoke deserializer with self.data, instead
        # of looking for it in the request, like the standard FolderPost
        self.data = data
        return data

    def before_deserialization(self, obj):
        field = IDocumentSchema['file']
        if obj.is_mail:
            field = IMail['message']

        namedblobfile = field._type(
            data=self.file_upload,
            contentType=self.content_type,
            filename=self.filename)

        field.set(field.interface(obj), namedblobfile)

    def before_serialization(self, obj):
        ILinkedDocuments(obj).link_gever_document(self.gever_document_uid)

    def add_object_to_context(self):

        super(UploadDocumentCopy, self).add_object_to_context()
        data = json.loads(self.request.form['document_metadata'])

        if self.obj.portal_type == 'opengever.document.document' and data.get("final", None):
            wftool = api.portal.get_tool('portal_workflow')
            chain = wftool.getChainFor(self.obj)
            workflow_id = chain[0]
            wftool.setStatusOf(workflow_id, self.obj, {
                'review_state': self.obj.final_state_workspace,
                'action': '',
                'actor': ''})
            workflow = wftool.getWorkflowById(workflow_id)
            workflow.updateRoleMappingsFor(self.obj)
            self.obj.reindexObject(idxs=['review_state'])
            self.obj.reindexObjectSecurity()
