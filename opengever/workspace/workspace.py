from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.ogds.base.sources import ActualWorkspaceMembersSourceBinder
from opengever.workspace import _
from opengever.workspace import is_todo_feature_enabled
from opengever.workspace import is_workspace_meeting_feature_enabled
from opengever.workspace.base import WorkspaceBase
from opengever.workspace.interfaces import IDeleter
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceSettings
from plone import api
from plone.autoform import directives
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from plone.supermodel import model
from zExceptions import Forbidden
from zExceptions import Unauthorized
from zope import schema
from zope.interface import implements
from zope.interface import provider
import uuid


def videoconferencing_url_default():
    """Concatenate base_url with a random UUID.

    This is built with jitsi in mind but might just work for other
    videoconferencing services.
    """
    base_url = api.portal.get_registry_record(
        'videoconferencing_base_url', interface=IWorkspaceSettings)
    if not base_url:
        return None

    return u'{}/{}'.format(base_url.rstrip('/'), uuid.uuid4())


@provider(IFormFieldProvider)
class IWorkspaceSchema(model.Schema):

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u"label_owner", default=u"Owner"),
        source=ActualWorkspaceMembersSourceBinder(),
        required=False,
    )
    videoconferencing_url = schema.TextLine(
        title=_(u'label_videoconferencing_url', default=u'Videoconferencing URL'),
        description=_(u'help_videoconferencing_url',
                      default=u'URL for videoconferencing link'),
        required=False,
        defaultFactory=videoconferencing_url_default
    )
    directives.omitted('external_reference')
    external_reference = schema.TextLine(
        title=_(u'label_linked_dossier', default=u'Linked dossier'),
        required=False,
        default=u'',
        missing_value=u''
    )


class Workspace(WorkspaceBase):
    implements(IWorkspace)

    def get_parent_with_local_roles(self):
        return self

    def allowedContentTypes(self, *args, **kwargs):
        types = super(Workspace, self).allowedContentTypes(*args, **kwargs)

        def filter_type(fti):
            if fti.id == "opengever.workspace.todo" or fti.id == "opengever.workspace.todolist":
                return is_todo_feature_enabled()
            if fti.id == "opengever.workspace.meeting":
                return is_workspace_meeting_feature_enabled()
            return True

        return filter(filter_type, types)

    def is_deletion_allowed(self):
        try:
            IDeleter(self).verify_may_delete()
            return True
        except Forbidden:
            return False


class WorkspaceContentPatch(ContentPatch):
    """Workspace specific PATCH service, which allows updating the content
    order without ModifyPortalContent permission. It checks instead for the
    specific `Update Content Order` permission
    """

    def reply(self):
        data = json_body(self.request)
        if data.keys() != ['ordering']:
            if data.keys() == ['external_reference']:
                if not api.user.has_permission('Modify portal content', obj=self.context):
                    raise Unauthorized()
            else:
                if not api.user.has_permission('opengever.workspace: Modify Workspace',
                                               obj=self.context):
                    raise Unauthorized()

        return super(WorkspaceContentPatch, self).reply()
