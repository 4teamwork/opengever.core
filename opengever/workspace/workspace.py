from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.interfaces import IDeleter
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSourceBinder
from opengever.workspace import _
from opengever.workspace import is_todo_feature_enabled
from opengever.workspace import is_workspace_meeting_feature_enabled
from opengever.workspace.base import WorkspaceBase
from opengever.workspace.browser.meeting_pdf import validate_header_footer
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceSettings
from plone import api
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedImage
from plone.restapi.deserializer import json_body
from plone.restapi.services.content.update import ContentPatch
from plone.schema import JSONField
from plone.supermodel import model
from zExceptions import Forbidden
from zExceptions import Unauthorized
from zope import schema
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
import json
import uuid


HEADER_FOOTER_FORMAT = json.dumps({
    'left': '',
    'center': '',
    'right': '',
})

FOOTER_DEFAULT_FORMAT = {
    'left': '{print_date}',
    'center': '',
    'right': '{page_number}/{number_of_pages}',
}


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

    directives.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u"label_owner", default=u"Owner"),
        source=WorkspaceContentMemberUsersSourceBinder(),
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
    directives.omitted('gever_url')
    gever_url = schema.TextLine(
        title=_(u'label_gever_url', default=u'GEVER URL'),
        required=False,
        default=u'',
        missing_value=u''
    )
    hide_members_for_guests = schema.Bool(
        title=_(u'label_hide_members_for_guests',
                default=u'Hide workspace members for workspace guests'),
        required=False,
    )
    meeting_template_header = JSONField(
        title=_(u'label_workspace_meeting_template_header',
                default=u'Meeting minutes header'),
        description=_(u'help_workspace_header_and_footer',
                      default=u'Dynamic content placeholders are {page_number}, '
                      u'{number_of_pages} and {print_date}, as well as the image '
                      u'placeholders {customer_logo} and {workspace_logo}'),
        schema=HEADER_FOOTER_FORMAT,
        required=False,
    )
    meeting_template_footer = JSONField(
        title=_(u'label_workspace_meeting_template_footer',
                default=u'Meeting minutes footer'),
        description=_(u'help_workspace_header_and_footer',
                      default=u'Dynamic content placeholders are {page_number}, '
                      u'{number_of_pages} and {print_date}, as well as the image '
                      u'placeholders {customer_logo} and {workspace_logo}'),
        schema=HEADER_FOOTER_FORMAT,
        default=dict(FOOTER_DEFAULT_FORMAT),
        required=False,
    )
    workspace_logo = NamedImage(
        title=_(u'label_workspace_logo', default='Workspace logo'),
        description=_(u'help_workspace_logo',
                      default=u'Can be used in headers and footers of meeting '
                      u'minutes'),
        required=False,
    )

    @invariant
    def validate_meeting_minutes_header_and_footer(data):
        try:
            validate_header_footer(data.meeting_template_header)
            validate_header_footer(data.meeting_template_footer)

        except KeyError as e:
            raise Invalid(
                _(u'msg_invalid_placholders_in_meeting_settings',
                  default=u'Invalid meeting minutes configuration, not '
                  u'supported placeholders "${placeholder}" are used.',
                  mapping={'placeholder': e.message}))


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

    def access_members_allowed(self):
        if self.hide_members_for_guests:
            return api.user.has_permission(
                'opengever.workspace: Access hidden members', obj=self)

        return True


class WorkspaceContentPatch(ContentPatch):
    """Workspace specific PATCH service, which allows updating the content
    order without ModifyPortalContent permission. It checks instead for the
    specific `Update Content Order` permission
    """

    def reply(self):
        data = json_body(self.request)
        if data.keys() != ['ordering']:
            if data.keys() == ['gever_url', 'external_reference']:
                if not api.user.has_permission('Modify portal content', obj=self.context):
                    raise Unauthorized()
            else:
                if not api.user.has_permission('opengever.workspace: Modify Workspace',
                                               obj=self.context):
                    raise Unauthorized()

        return super(WorkspaceContentPatch, self).reply()
