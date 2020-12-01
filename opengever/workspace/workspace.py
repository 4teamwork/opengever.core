from opengever.workspace import _
from opengever.workspace.base import WorkspaceBase
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceSettings
from plone import api
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from plone.supermodel import model
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
