from collective import dexteritytextindexer
from opengever.workspace.interfaces import IWorkspaceMeeting
from opengever.workspace.workspace import IWorkspaceSchema
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.indexer import indexer
from Products.CMFDiffTool.utils import safe_utf8
from zope.component import adapter
from zope.interface import implementer


@indexer(IWorkspaceSchema)
def external_reference(obj):
    if obj.external_reference:
        return obj.external_reference
    return ''


INDEXED_IN_MEETING_SEARCHABLE_TEXT = ['title', 'text', 'decision']


def to_safe_utf8(obj, fieldname):
    value = getattr(obj, fieldname)
    if value is None:
        return
    if isinstance(value, RichTextValue):
        value = api.portal.get_tool(name='portal_transforms').convertTo(
            'text/plain', value.output, mimetype='text/html').getData()
    return safe_utf8(value)


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
@adapter(IWorkspaceMeeting)
class WorkspaceMeetingSearchableTextExtender(object):
    """This extender includes the WorkspaceMeetingAgendaItems in the
    WorkspaceMeeting SearchableText.

    The searchable text gets updated when WorkspaceMeetingAgendaItems are added
    or modified via event handles (see workspace_meeting_agendaitem_added, and
    workspace_meeting_agendaitem_modified)."""

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []

        # We include the WorkspaceMeetingAgendaItems in the the searchable text
        # of the meeting.
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog.unrestrictedSearchResults(
            path=path,
            portal_type='opengever.workspace.meetingagendaitem')

        for brain in brains:
            agendaitem = brain.getObject()
            searchable.extend(
                [to_safe_utf8(agendaitem, fieldname) for fieldname
                 in INDEXED_IN_MEETING_SEARCHABLE_TEXT])

        return ' '.join(filter(None, searchable))


@indexer(IWorkspaceMeeting)
def attendees(obj):
    return obj.attendees


@indexer(IWorkspaceSchema)
def hide_member_details(obj):
    return bool(obj.hide_members_for_guests)
