from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base import _
from opengever.ogds.base.sources import CurrentAdminUnitOrgUnitsSourceBinder
from opengever.ogds.base.sources import AllFilteredGroupsSourceBinder
from opengever.ogds.models import UNIT_TITLE_LENGTH
from opengever.ogds.models.team import Team
from plone.autoform import directives as form
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel import model
from z3c.form import field
from zope import schema


class ITeam(model.Schema):

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
        source=AllFilteredGroupsSourceBinder(),
        required=True)

    form.widget('org_unit_id', KeywordFieldWidget, async=True)
    org_unit_id = schema.Choice(
        title=_('label_org_unit', default=u'Org Unit'),
        source=CurrentAdminUnitOrgUnitsSourceBinder(),
        required=True)


class TeamAddForm(ModelAddForm):

    schema = ITeam
    model_class = Team

    label = _('label_add_team', default=u'Add team')


class TeamEditForm(ModelEditForm):

    fields = field.Fields(ITeam)
    model_class = Team

    label = _('label_edit_team', default=u'Edit team')

    fields['groupid'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True)

    fields['org_unit_id'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True)

    def __init__(self, context, request):
        super(TeamEditForm, self).__init__(context, request, context.model)

    def nextURL(self):
        return get_contactfolder_url()

    def updateWidgets(self):
        super(TeamEditForm, self).updateWidgets()
