from AccessControl.unauthorized import Unauthorized
from opengever.api.add import GeverFolderPost
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.base.handlers import ObjectTouchedEvent
from opengever.base.oguid import Oguid
from opengever.base.sentry import maybe_report_exception
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.versioner import Versioner
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.utils import get_main_dossier
from opengever.journal.handlers import journal_entry_factory
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.ogds.base.actor import Actor
from opengever.workspaceclient import _
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import CopyFromWorkspaceForbidden
from opengever.workspaceclient.exceptions import CopyToWorkspaceForbidden
from opengever.workspaceclient.exceptions import FolderNotFound
from opengever.workspaceclient.exceptions import GeverDocumentCantBeChanged
from opengever.workspaceclient.exceptions import WorkspaceNotFound
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedDocuments
from opengever.workspaceclient.interfaces import ILinkedToWorkspace
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.locking.interfaces import ILockable
from plone.memoize import ram
from plone.restapi.interfaces import ISerializeToJson
from requests import HTTPError
from time import time
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
import sys
import transaction


CACHE_TIMEOUT = 24 * 60 * 60

RETRIEVAL_MODE_COPY = 'copy'
RETRIEVAL_MODE_VERSION = 'version'


def list_cache_key(linked_workspaces_instance, **kwargs):
    """Cache key builder for linked workspaces list.
    This cache key is per user and will get invalidated every CACHE_TIMEOUT,
    when a workspace is linked or removed from a dossier or when CACHE_TIMEOUT
    is modified.
    It also depends on additional parameters which should be btaching parameters
    of the request.
    """
    uid = linked_workspaces_instance.context.UID()
    linked_workspace_uids = '-'.join(linked_workspaces_instance.storage.list())
    userid = api.user.get_current().getId()
    timeout_key = str(time() // CACHE_TIMEOUT if CACHE_TIMEOUT > 0 else str(time()))

    cache_key = '-'.join(('linked_workspaces_storage', userid, uid,
                          linked_workspace_uids, str(CACHE_TIMEOUT), timeout_key))

    keywordarguments = '-'.join('{}={}'.format(key, value) for key, value in kwargs.items())
    if keywordarguments:
        cache_key = '{}-{}'.format(cache_key, keywordarguments)

    return cache_key


class ProxyPost(GeverFolderPost):
    """When copying a document back from Workspace into GEVER, we GET the
    document from the workspace so that we have the serialized data. We then
    need to deserialize this to create a new object in the dossier. The process
    needed for this creation is the same as in a POST request to GEVER (i.e.
    create an object in the void, get the correct deserializer and deserialize
    the data into the object, add the object to the context), except
    that we already have the data and do not need to get it from the request.
    This class allows us to reuse GeverFolderPost by simply overwriting how we
    get the serialized data.
    """
    def __init__(self, data):
        self._request_data = data

    @property
    def request_data(self):
        """We have the serialized data from a previous GET request,
        and it is not contained in the request as it would be for a
        normal POST.
        """
        return self._request_data

    def serialize_object(self):
        """The reply here is not sent back to the user, so we do not
        need to serialize the object, but rather return the object itself.
        """
        return self.obj


@implementer(ILinkedWorkspaces)
@adapter(IDossierMarker)
class LinkedWorkspaces(object):
    """Manages linked workspaces for an object.
    """

    def __init__(self, context):
        self.client = WorkspaceClient()
        self.storage = LinkedWorkspacesStorage(context)
        self.context = context

    @ram.cache(lambda method, context, **kwargs: list_cache_key(context, **kwargs))
    def list(self, **kwargs):
        """Returns a JSON summary-representation of all stored workspaces.
        This function lookups all UIDs on the remote system by dispatching a
        search requests to the remote system.
        This means, unauthorized objects or not existing UIDs will be skipped
        automatically.
        """
        return self.list_non_cached(**kwargs)

    def list_non_cached(self, **kwargs):
        uids = self.storage.list()
        if not uids:
            return {'items': [], 'items_total': 0}

        return self.client.search(
            UID=uids,
            portal_type="opengever.workspace.workspace",
            metadata_fields="UID",
            **kwargs)

    def number_of_linked_workspaces(self):
        return len(self.storage.list())

    def create(self, **data):
        """Creates a new workspace an links it with the current dossier.

        This function returns the serialized workspace.
        """
        if isinstance(data, dict):
            oguid = Oguid.for_object(self.context).id
            data['external_reference'] = oguid
            data['gever_url'] = self.client.get_gever_url(oguid)
        workspace = self.client.create_workspace(**data)
        self.storage.add(workspace.get('UID'))
        if not ILinkedToWorkspace.providedBy(self.context):
            alsoProvides(self.context, ILinkedToWorkspace)
            self.context.reindexObject(idxs=['object_provides'])

        # Add journal entry to dossier
        title = _(
            u'label_linked_workspace_created',
            default=u'Linked workspace ${workspace_title} created.',
            mapping={'workspace_title': workspace.get('title')})

        journal_entry_factory(
            context=self.context, action='Linked workspace created',
            title=title)

        return workspace

    def link_to_workspace(self, workspace_uid):
        workspace = self.client.link_to_workspace(
            workspace_uid, Oguid.for_object(self.context).id)

        self.storage.add(workspace.get('UID'))

        if not ILinkedToWorkspace.providedBy(self.context):
            alsoProvides(self.context, ILinkedToWorkspace)
            self.context.reindexObject(idxs=['object_provides'])

        # Add journal entry to dossier
        title = _(
            u'label_workspace_linked',
            default=u'Linked to workspace ${workspace_title}.',
            mapping={'workspace_title': workspace.get('title')})

        journal_entry_factory(
            context=self.context, action='Linked to workspace',
            title=title)

    def unlink_workspace(self, workspace_uid, deactivate_workspace=False):
        if workspace_uid not in self.storage.list():
            raise BadRequest(
                'Workspace with UID {} is not connected'.format(workspace_uid))

        workspace = self.client.unlink_workspace(workspace_uid)

        # cleanup document locks
        try:
            docs = self.get_documents_linked_with_workspace(workspace['@id'])
        except Unauthorized:
            raise BadRequest(
                'You are not allowed to access and unlock all linked '
                'documents, unlinking this workspace is not possible.')

        for doc in docs:
            ILockable(doc).unlock(COPIED_TO_WORKSPACE_LOCK)

        self.storage.remove(workspace_uid)
        if len(self.storage.list()) == 0:
            noLongerProvides(self.context, ILinkedToWorkspace)
            self.context.reindexObject(idxs=['object_provides'])

        # Add journal entry to dossier
        title = _(
            u'label_workspace_unlinked',
            default=u'Unlinked workspace ${workspace_title}.',
            mapping={'workspace_title': workspace.get('title')})

        journal_entry_factory(
            context=self.context, action='Unlinked workspace',
            title=title)

        if deactivate_workspace:
            workspace_url = workspace.get('@id').strip('/')
            raise_bad_request = False
            try:
                if self.client.is_workspace_deactivation_transition_available(workspace_url):
                    self.client.deactivate_workspace(workspace_url)
                else:
                    raise_bad_request = True
            except HTTPError:
                e_type, e_value, tb = sys.exc_info()
                maybe_report_exception(self.context, self.context.REQUEST, e_type, e_value, tb)
                raise_bad_request = True

            if raise_bad_request:
                # We need to commit the transaction because the workspace is already unlinked
                # and in case of a rollback only the dossier would remain linked.
                transaction.commit()
                raise NotReportedBadRequest(
                    _(u"deactivate_workspace_failed",
                      default=u"The workspace was unlinked, but it could not be deactivated."))

    def _get_linked_workspace_url(self, workspace_uid):
        if workspace_uid not in self.storage:
            raise WorkspaceNotLinked()

        workspace_url = self.client.lookup_url_by_uid(workspace_uid)

        if not workspace_url:
            raise WorkspaceNotFound()
        return workspace_url

    def _get_folder_url(self, folder_uid):
        folder_url = self.client.lookup_url_by_uid(folder_uid)

        if not folder_url:
            raise FolderNotFound()

        return folder_url

    def copy_document_to_workspace(self, document, workspace_uid, lock=False, folder_uid=None):
        """Will upload a copy of a document to a linked workspace.

        If a `folder_uid` is provided, the document will be uploaded to that
        folder in the workspace (that folder must be inside the linked
        workspace identified by `workspace_uid`).

        Otherwise, the document is uploaded into the root of the workspace.
        """
        if document.is_checked_out():
            raise CopyToWorkspaceForbidden(
                "Document %r can't be copied to a workspace because it's "
                "currently checked out" % document)

        workspace_url = self._get_linked_workspace_url(workspace_uid)

        folder_url = None
        if folder_uid:
            folder_url = self._get_folder_url(folder_uid)

        file_ = document.get_file()
        document_repr = self._serialized_document_schema_fields(document)
        document_metadata = self._drop_non_metadata_fields(document_repr)

        target_url = workspace_url
        if folder_url:
            target_url = folder_url

        if not file_:
            # File only preserved in paper. Not linked to GEVER document,
            # since there's no file that could be transferred back.
            return self.client.post(target_url, json=document_repr)

        document_metadata['gever_url'] = self.client.get_gever_url(Oguid.for_object(document).id)
        document_metadata['final'] = document.is_final_document()

        filename = document.get_filename()
        gever_document_uid = document.UID()

        # Add journal entry to dossier
        workspace_title = self.client.get_by_uid(workspace_uid).get('title')
        title = _(
            u'label_document_copied_to_workspace',
            default=u'Document ${doc_title} copied to workspace ${workspace_title}.',
            mapping={'doc_title': document.title_or_id(),
                     'workspace_title': workspace_title})

        journal_entry_factory(
            context=self.context, action='Document copied to workspace',
            title=title, documents=[document])

        response = self.client.upload_document_copy(
            target_url, file_.open(),
            file_.contentType, filename,
            document_metadata, gever_document_uid)

        workspace_document_uid = response['UID']
        ILinkedDocuments(document).link_workspace_document(workspace_document_uid)

        if lock and not document.is_mail:
            ILockable(document).lock(COPIED_TO_WORKSPACE_LOCK)
        return response

    def _get_document_by_uid(self, workspace_uid, document_uid):
        linked_documents = self.list_documents_in_linked_workspace(workspace_uid, UID=document_uid)
        if linked_documents.get('items_total') == 1:
            return linked_documents['items'][0]

    def copy_document_from_workspace(
            self, workspace_uid, document_uid,
            as_new_version=False, trash_tr_document=False):
        """Will copy a document from a linked workspace.
        """
        document = self._get_document_by_uid(workspace_uid, document_uid)
        if not document:
            raise LookupError("Document not in linked workspace")

        if bool(document['checked_out']):
            raise CopyFromWorkspaceForbidden(
                "Document %r can't be copied from workspace because it's "
                "currently checked out" % document_uid)

        document_url = document.get("@id")
        document_repr = self.client.get(url_or_path=document_url)

        if document_repr.get('archival_file'):
            data = self.client.request.get(document_repr['archival_file']['download'])
            document_repr['archival_file']['data'] = data.content
        if document_repr.get('file'):
            data = self.client.request.get(document_repr['file']['download'])
            document_repr['file']['data'] = data.content
        elif document_repr.get('original_message'):
            # The deserializer will copy the file in message back to
            # original_message and transform it back to an eml and store it
            # in message. Writing the original_message directly would require
            # manager permissions.
            data = self.client.request.get(document_repr['original_message']['download'])
            document_repr['message'] = document_repr.pop('original_message')
            document_repr['message']['data'] = data.content
        elif document_repr.get('message'):
            data = self.client.request.get(document_repr['message']['download'])
            document_repr['message']['data'] = data.content

        # We should avoid setting the id ourselves, can lead to conflicts
        document_repr = self._blacklisted_dict(document_repr, ['id', 'gever_url'])

        workspace_title = self.client.get_by_uid(workspace_uid).get('title')

        # If the workspace document doesn't have a link to a GEVER document,
        # or is not a regular document with a file, or cannot be retrieved,
        # for example because the GEVER document was trashed, always create
        # a copy instead of attempting to create a version.
        gever_doc = self._get_corresponding_gever_doc(document_repr)

        if gever_doc and gever_doc.is_final_document():
            raise GeverDocumentCantBeChanged(
                "Document %r can't be copied from workspace because "
                "Gever Document is finalized" % gever_doc)

        is_document_with_file = all((
            document_repr['@type'] == u'opengever.document.document',
            document_repr.get('file')))

        if as_new_version and gever_doc and is_document_with_file:
            retrieval_mode = RETRIEVAL_MODE_VERSION
            gever_doc = self._retrieve_as_version(document_repr, gever_doc, workspace_title)
        else:
            retrieval_mode = RETRIEVAL_MODE_COPY
            gever_doc = self._retrieve_as_copy(document_repr, workspace_title)

        if trash_tr_document:
            try:
                self.client.trash_document(document_url)
            except HTTPError:
                # Commit txn so that raising BadRequest does not rollback
                # the already successully transferred document
                transaction.commit()
                raise BadRequest(
                    _("Not moved to trash: Document was retrieved, but "
                      "workspace document could not be moved to trash."))

        return gever_doc, retrieval_mode

    @staticmethod
    def _get_corresponding_gever_doc(document_repr):
        gever_doc_link = document_repr.get('teamraum_connect_links', {}).get('gever_document')
        gever_doc_uid = gever_doc_link.get('UID') if gever_doc_link else None
        if not gever_doc_uid:
            return

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(UID=gever_doc_uid)
        gever_doc = results[0].getObject() if results else None
        return gever_doc

    def _retrieve_as_version(self, document_repr, gever_doc, workspace_title):
        # Make sure the previous working copy is saved as an initial
        # version. This MUST happen before updating the file.
        Versioner(gever_doc).create_initial_version()

        version_comment = _(u'document_retrieved_from_teamraum_change_note',
                            default=u'Document retrieved from teamraum')
        gever_doc.update_file(
            document_repr['file']['data'],
            content_type=document_repr['file']['content-type'],
            filename=document_repr['file']['filename'],
            create_version=True,
            comment=translate(version_comment, context=getRequest()))

        # Dossier
        journal_entry_factory(
            context=self.context,
            action='Document retrieved from teamraum',
            title=_(
                u'label_document_retrieved_from_workspace',
                default=u'Document ${doc_title} retrieved from workspace.',
                mapping={'doc_title': document_repr.get('title')})
        )

        # Document
        journal_entry_factory(
            context=gever_doc,
            action='Document retrieved as new version from teamraum',
            title=_(
                u'label_document_retrieved_as_new_version_from_teamraum',
                default=u'Document unlocked - created new version with '
                        u'document from teamraum.')
        )

        notify(ObjectCheckedInEvent(gever_doc, '', suppress_journal_entry_creation=True))
        notify(ObjectTouchedEvent(gever_doc))
        ILockable(gever_doc).unlock(COPIED_TO_WORKSPACE_LOCK)
        return gever_doc

    def _retrieve_as_copy(self, document_repr, workspace_title):
        proxy_post = ProxyPost(document_repr)
        proxy_post.context = self.context
        proxy_post.request = getRequest()
        gever_doc = proxy_post.reply()

        # Dossier
        journal_entry_factory(
            context=self.context,
            action='Document copied from workspace',
            title=_(
                u'label_document_copied_from_workspace',
                default=u'Document ${doc_title} copied from workspace '
                        u'${workspace_title} as a new document.',
                mapping={'doc_title': document_repr.get('title'),
                         'workspace_title': workspace_title})
        )

        # Document
        journal_entry_factory(
            context=gever_doc,
            action='Document created via copy from teamraum',
            title=_(
                u'label_initial_version_document_copied_from_teamraum',
                default=u'Initial version - Document copied from teamraum '
                        u'${workspace_title}.',
                mapping={'workspace_title': workspace_title})
        )

        return gever_doc

    def list_documents_in_linked_workspace(self, workspace_uid, **kwargs):
        """List documents contained in a linked workspace
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)

        return self.client.search(
            url_or_path=workspace_url,
            portal_type=["opengever.document.document", "ftw.mail.mail"],
            metadata_fields=["UID", "filename", "checked_out"],
            **kwargs)

    def get_documents_linked_with_workspace(self, workspace_url):
        """Returns a list of gever documents wich are linked with
        the given workspace.
        """

        result = self.client.request.get(
            '{}/@list-linked-gever-documents-uids'.format(workspace_url))
        uids = result.json().get('gever_doc_uids', [])

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            path='/'.join(self.context.getPhysicalPath()),
            UID=uids)

        return [brain.getObject() for brain in brains]

    def has_linked_workspaces(self):
        """Returns true if the current context has linked workspaces
        """
        return self.number_of_linked_workspaces() > 0

    def move_workspace_links_to_main_dossier(self):
        """Called by event handler when a dossier gets moved in to a subdossier.
        """
        main_dossier = get_main_dossier(self.context)
        if main_dossier == self.context:
            # dossier is still a main dossier no need for change
            return

        main_dossier_oguid = Oguid.for_object(main_dossier).id
        main_dossier_linked_workspace = ILinkedWorkspaces(main_dossier)

        uids = self.storage.list()
        for workspace_uid in uids:
            try:
                self.client.update_dossier_uid(workspace_uid, main_dossier_oguid)
            except Exception:
                raise Exception(
                    u'Linked workspaces could not be updated, '
                    'moving this dossier into a dossier not possible.')

        self.storage.remove(workspace_uid)
        noLongerProvides(self.context, ILinkedToWorkspace)
        self.context.reindexObject(idxs=['object_provides'])

        main_dossier_linked_workspace.storage.add(workspace_uid)
        if not ILinkedToWorkspace.providedBy(self.context):
            alsoProvides(main_dossier, ILinkedToWorkspace)
            main_dossier.reindexObject(idxs=['object_provides'])

    def _form_fields(self, obj):
        """Returns a list of all form field names of the given object.
        """
        fieldnames = []
        for schema in iterSchemata(obj):
            for fieldname in schema:
                fieldnames.append(fieldname)
        return fieldnames

    def _serialized_document_schema_fields(self, document):
        """Serializes all document schema fields.
        """
        serializer = getMultiAdapter((document, self.context.REQUEST), ISerializeToJson)
        whitelist = self._form_fields(document)
        whitelist.append('@type')
        return self._whitelisted_dict(serializer(), whitelist)

    def _drop_non_metadata_fields(self, serialized_document):
        """Drops non-metadata fields from a serialized document in order to
        prepare it as needed by the @upload-document-copy endpoint.
        """
        return self._blacklisted_dict(
            serialized_document,
            ['file', 'archival_file', 'message', 'original_message', 'relatedItems'])

    def _whitelisted_dict(self, dict_obj, whitelist):
        whitelisted_dict = {}
        for key in whitelist:
            if key in dict_obj:
                whitelisted_dict[key] = dict_obj[key]
        return whitelisted_dict

    def _blacklisted_dict(self, dict_obj, blacklist):
        blacklisted_dict = {}
        for key in dict_obj.keys():
            if key in blacklist:
                continue
            blacklisted_dict[key] = dict_obj[key]

        return blacklisted_dict

    def add_participations(self, workspace_uid, participations):
        """ Adds participations on the workspace
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)
        participations_by_name = []
        for participation in participations:
            actor = Actor.lookup(participation['participant'], name_as_fallback=True)
            participations_by_name.append({
                u'participant': actor.login_name,
                u'role': participation[u'role'],
            })
        return self.client.post(
            '{}/@participations'.format(workspace_url),
            json={'participants': participations_by_name})

    def add_invitation(self, workspace_uid, invitation_data):
        """ Adds an invitation on the workspace
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)
        return self.client.post(
            '{}/@invitations'.format(workspace_url),
            json=invitation_data)
