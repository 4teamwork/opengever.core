from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.inbox import _
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema


class IInbox(form.Schema, ITabbedviewUploadable):
    """ Inbox for OpenGever
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'inbox_group', ],
    )

    inbox_group = schema.TextLine(
        title=_(u'label_inbox_group', default=u'Inbox Group'),
        description=_(u'help_inbox_group', default=u''),
        required=False,
    )


class Inbox(Container):

    def get_current_inbox(self):
        """Returns the subinbox of the current orgUnit if exists,
        otherwise the inbox itself."""

        sub_inboxes = self.listFolderContents(
            contentFilter={'portal_type':'opengever.inbox.inbox'})

        for inbox in sub_inboxes:
            if inbox.get_responsible_org_unit() == get_current_org_unit():
                return inbox

        return self

    def get_responsible_org_unit(self):
        """Returns the OrgUnit object, which is configured in the
        ResponsibleOrgUnit behavior field."""

        org_unit_id = IResponsibleOrgUnit(self).responsible_org_unit
        if org_unit_id:
            return ogds_service().fetch_org_unit(org_unit_id)

        return None

    def is_main_inbox(self):
        """A main inbox is a inbox container when:
         - Is a root inbox
         - Is not assigned to a org unit(responsible_org_unit)
        """
        if not IInbox.providedBy(aq_parent(aq_inner(self))):
            return IResponsibleOrgUnit(self).responsible_org_unit == None

        return False

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
        return '/'.join(url_tool.getRelativeContentPath(self))
