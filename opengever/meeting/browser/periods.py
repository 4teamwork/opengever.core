from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.browser.modelforms import ModelEditForm
from opengever.meeting import _
from opengever.tabbedview import GeverTabMixin
from plone import api
from plone.autoform import directives as form
from plone.supermodel import model
from Products.Five.browser import BrowserView
from zope import schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class IPeriodModel(model.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        max_length=256,
        required=True)

    form.widget(date_from=DatePickerFieldWidget)
    date_from = schema.Date(
        title=_('label_date_from', default='Start date'),
        required=True,
    )

    form.widget(date_to=DatePickerFieldWidget)
    date_to = schema.Date(
        title=_('label_date_to', default='End date'),
        required=True,
    )


class EditPeriod(ModelEditForm):

    label = _('label_edit_period', default=u'Edit Period')

    schema = IPeriodModel

    def __init__(self, context, request):
        super(EditPeriod, self).__init__(context, request, context.model)

    def nextURL(self):
        return "{}#periods".format(
            aq_parent(aq_inner(self.context)).absolute_url())


class PeriodsTab(BrowserView, GeverTabMixin):

    show_searchform = False

    template = ViewPageTemplateFile('templates/periods.pt')

    def __call__(self):
        return self.template()

    def get_periods(self):
        """Returns all periods for the current committee.
        """
        return api.content.find(
            context=self.context,
            portal_type='opengever.meeting.period',
            sort_on='start',
            sort_order='descending')

    def get_localized_time(self, dt):
        return api.portal.get_localized_time(datetime=dt)

    def is_editable_by_current_user(self):
        """Return whether the current user can edit periods."""

        return api.user.has_permission(
            'Modify portal content', obj=self.context)

    def is_manager(self):
        return api.user.has_permission('cmf.ManagePortal')
