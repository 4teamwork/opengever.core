from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.browser.modelforms import ModelAddForm
from opengever.ogds.base import _
from opengever.ogds.base.sources import AllGroupsSourceBinder
from opengever.ogds.base.sources import AllOrgUnitsSourceBinder
from opengever.ogds.models import UNIT_TITLE_LENGTH
from opengever.ogds.models.team import Team
from plone.directives import form
from zope import schema


class ITeam(form.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=UNIT_TITLE_LENGTH)

    active = schema.Bool(
        title=_(u"label_active", default=u"Active"),
        required=True,
        default=True)

    form.widget('groupid', KeywordFieldWidget, async=True)
    groupid = schema.Choice(
        title=_('label_group', default=u'Group'),
        source=AllGroupsSourceBinder(),
        required=True)

    form.widget('org_unit_id', KeywordFieldWidget, async=True)
    org_unit_id = schema.Choice(
        title=_('label_org_unit', default=u'Org Unit'),
        source=AllOrgUnitsSourceBinder(),
        required=True)


class TeamAddForm(ModelAddForm):

    schema = ITeam
    model_class = Team

    label = _('label_add_team', default=u'Add team')
