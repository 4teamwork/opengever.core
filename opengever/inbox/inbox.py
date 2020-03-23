from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.inbox import _
from opengever.ogds.models.service import ogds_service
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema


class IInbox(model.Schema, ITabbedviewUploadable):
    """ Inbox for OpenGever
    """

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'inbox_group', ],
    )

    inbox_group = schema.TextLine(
        title=_(u'label_inbox_group', default=u'Inbox Group'),
        description=_(u'help_inbox_group', default=u''),
        required=False,
    )


class Inbox(Container, TranslatedTitleMixin):

    Title = TranslatedTitleMixin.Title

    def get_responsible_org_unit(self):
        """Returns the OrgUnit object, which is configured in the
        ResponsibleOrgUnit behavior field."""

        org_unit_id = IResponsibleOrgUnit(self).responsible_org_unit
        if org_unit_id:
            return ogds_service().fetch_org_unit(org_unit_id)

        return None

    def get_sequence_number(self):
        """The Inbox does not have a sequence number."""

        return None
