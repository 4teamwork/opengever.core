from datetime import date
from five import grok
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.meeting import _
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.committee import ICommittee
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.meeting.model import Period
from plone.directives import form
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.interfaces import IDataConverter
from zope import schema
from zope.component import getUtility


class IPeriodModel(form.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        max_length=256,
        required=True)

    date_from = schema.Date(
        description=_('label_date_from', default='Start date'),
        required=True,
    )

    date_to = schema.Date(
        description=_('label_date_to', default='End date'),
        required=True,
    )


CLOSE_PERIOD_STEPS = (
    ('close-period', _(u'Close period')),
    ('add-period', _(u'Add new period'))
)


def get_dm_key(committee):
    """Return the key used to store data in the wizard-storage."""

    return 'close_period:{}'.format(committee.committee_id)


class CloseCurrentPeriodStep(BaseWizardStepForm, ModelEditForm):
    """Form to close the current period.

    First part of a two-step wizard. Stores its data in IIWizardStorage when
    submitted.

    """
    step_name = 'close-period'
    label = _('Close period')
    step_title = _('Close currently active period')
    steps = CLOSE_PERIOD_STEPS

    fields = Fields(IPeriodModel)

    def __init__(self, context, request):
        self.committee = context.load_model()
        model = Period.query.get_current(self.committee)
        super(CloseCurrentPeriodStep, self).__init__(
            context, request, model)

    def get_edit_values(self, keys):
        return self.model.get_edit_values(keys)

    def partition_data(self, data):
        obj_data, model_data = {}, data
        return obj_data, model_data

    def update_model(self, model_data):
        self.model.update_model(model_data)

    @buttonAndHandler(_(u'button_close_period',
                        default=u'Close period'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        dm = getUtility(IWizardDataStorage)
        dm.update(get_dm_key(self.committee), data)

        return self.request.RESPONSE.redirect(
            '{}/add-period'.format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def nextURL(self):
        return self._created_object.get_url()


class CloseCurrentPeriodStepView(FormWrapper, grok.View):
    """View to render the form to close a period."""

    grok.context(ICommittee)
    grok.name('close-period')
    grok.require('cmf.ModifyPortalContent')
    form = CloseCurrentPeriodStep

    def __init__(self, *args, **kwargs):
         FormWrapper.__init__(self, *args, **kwargs)
         grok.View.__init__(self, *args, **kwargs)

    def available(self):
        return is_meeting_feature_enabled()


class AddNewPeriodStep(BaseWizardStepForm, ModelAddForm):
    """Form to add a new period to an existing committee.

    Second part of a two-step wizard. Loads data from IIWizardStorage to
    update the period to close when submitted.

    """
    step_name = 'add-period'
    label = _('Add period')
    step_title = _('Add new period')
    steps = CLOSE_PERIOD_STEPS

    schema = IPeriodModel

    model_class = Period

    def __init__(self, context, request):
        self.committee = context.load_model()
        self.period_to_close = Period.query.get_current(self.committee)
        super(AddNewPeriodStep, self).__init__(context, request)

    def updateWidgets(self):
        super(AddNewPeriodStep, self).updateWidgets()
        self.inject_default_values()

    def inject_default_values(self):
        today = date.today()
        title = self.widgets['title']
        date_from = self.widgets['date_from']
        date_to = self.widgets['date_to']

        if not title.value:
            title.value = unicode(today.year)
        if not date_from.value:
            date_from.value = IDataConverter(date_from).toWidgetValue(
                date(today.year, 1, 1))
        if not date_to.value:
            date_to.value = IDataConverter(date_to).toWidgetValue(
                date(today.year, 12, 31))

    def create(self, data):
        self.close_previous_period()

        period = super(AddNewPeriodStep, self).create(data)
        period.committee = self.committee
        return period

    def close_previous_period(self):
        dm = getUtility(IWizardDataStorage)
        data = dm.get_data(get_dm_key(self.committee))

        self.period_to_close.update_model(data)
        self.period_to_close.execute_transition('active-closed')

        dm.drop_data(get_dm_key(self.committee))


class AddNewPeriodStepView(FormWrapper, grok.View):
    """View to render the form to create a new period."""

    grok.context(ICommittee)
    grok.name('add-period')
    grok.require('cmf.AddPortalContent')
    form = AddNewPeriodStep

    def __init__(self, *args, **kwargs):
         FormWrapper.__init__(self, *args, **kwargs)
         grok.View.__init__(self, *args, **kwargs)

    def available(self):
        return is_meeting_feature_enabled()
