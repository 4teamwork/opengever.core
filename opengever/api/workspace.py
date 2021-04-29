from Acquisition import aq_chain
from Acquisition import aq_parent
from ftw.mail.mail import IMail
from opengever.api.add import GeverFolderPost
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.actor import Actor
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceRoot
from opengever.workspace.participation import can_manage_member
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
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

        user_id = self.context.Creator()
        actor = Actor.lookup(user_id)
        result["responsible"] = {
            "title": actor.get_label(),
            "token": user_id,
        }
        result["responsible_fullname"] = actor.get_label(with_principal=False)

        return result


class UploadDocumentCopy(GeverFolderPost):
    """Endpoint to upload a complete copy of a GEVER document to a workspace.

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


class DeleteWorkspaceContent(Service):
    """Deletes workspace content

    Use this class for the DELETE endpoint for any deletable workspace content to
    be able to override the delete permission.

    This is necessary due to a special workflow implementation which is required
    to provide the activate/deactivate feature of a workspace.

    See https://github.com/4teamwork/opengever.core/pull/6620 for more information
    """
    def reply(self):
        if not self.is_within_workspace_root():
            raise Unauthorized()

        parent = aq_parent(self.context)
        try:
            parent._delObject(self.context.getId())
        except LinkIntegrityNotificationException:
            pass

        return self.reply_no_content()

    def is_within_workspace_root(context):
        """ Checks, if the content is within the workspace root.

        We have to be sure that we can't delete a content with this endpoint
        outside of the teamraum.
        """
        return bool(filter(IWorkspaceRoot.providedBy, aq_chain(context)))
