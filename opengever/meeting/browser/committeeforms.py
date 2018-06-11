from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.meeting import _
from opengever.meeting.browser.periods import IPeriodModel
from opengever.meeting.committee import Committee
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.model import Period
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.layout import FormWrapper
from Products.CMFCore.interfaces import IFolderish
from z3c.form import button
from z3c.form import field
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.interfaces import IDataConverter
from zope.component import adapter
from zope.component import getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


ADD_COMMITTEE_STEPS = (
    ('add-committee', _(u'Add committee')),
    ('add-period', _(u'Add period'))
)


def get_dm_key(context):
    container_oguid = Oguid.for_object(context)
    return 'create_committee:{}'.format(container_oguid)


class AddForm(BaseWizardStepForm, add.DefaultAddForm):
    """Form to create a committee.

    Is registered as default add form for committees. Does not create the
    committee when submitted but store its data in IIWizardStorage. Then
    redirects to the second step to add an initial period.

    """
    fields = field.Fields(Committee.model_schema)
    label = _('Add committee')

    step_name = 'add-meeting-dossier'
    steps = ADD_COMMITTEE_STEPS

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        dm = getUtility(IWizardDataStorage)
        dm.update(get_dm_key(self.context), data)

        return self.request.RESPONSE.redirect(
            "{}/add-initial-period".format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(add.DefaultAddView):
    form = AddForm


class AddInitialPeriodStep(BaseWizardStepForm, ModelProxyAddForm, add.DefaultAddForm):
    """Form to add an initial period during committee creation.

    Second part of a two-step wizard. Loads data from IIWizardStorage to
    also create the committee from the first step after successful submission.

    This form extends from dexterity's DefaultAddForm to create the plone
    content-type easily. To avoid duplicating DefaultAddForm.create we swap
    this form's fields during createAndAdd, i.e. after validation was
    successful.

    Does not extend from dexterity.AddForm to avoid auto-registering this
    form as add-form for committees, this would conflict with the form
    from the first step. Instead configure portal_type manually.

    """
    step_name = 'add-period'
    label = _('Add period')
    steps = ADD_COMMITTEE_STEPS

    portal_type = 'opengever.meeting.committee'
    content_type = Committee
    schema = IPeriodModel
    fields = Fields(IPeriodModel)
    fields['date_from'].widgetFactory = DatePickerFieldWidget
    fields['date_to'].widgetFactory = DatePickerFieldWidget

    @property
    def additionalSchemata(self):
        return []

    def updateWidgets(self):
        super(AddInitialPeriodStep, self).updateWidgets()
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

    def createAndAdd(self, data):
        """Remember data for period and inject committee data from previous
        form.

        """
        # switch fields when creating, use committee content-type fields to
        # create the plone object.
        self.fields = Fields(Committee.content_schema)

        dm = getUtility(IWizardDataStorage)
        committee_data = dm.get_data(get_dm_key(self.context))

        committee = super(AddInitialPeriodStep, self).createAndAdd(
            committee_data)

        self.create_period(committee, data)

        dm.drop_data(get_dm_key(self.context))
        return committee

    def create_period(self, committee, data):
        session = create_session()
        data.update({'committee': committee.load_model()})
        period = Period(**data)
        session.add(period)
        session.flush()  # required to immediately create an autoincremented id


class AddInitialPeriodStepView(FormWrapper):
    """View to render the form to close a period."""

    form = AddInitialPeriodStep


class EditForm(ModelProxyEditForm, edit.DefaultEditForm):

    fields = field.Fields(Committee.model_schema, ignoreContext=True)
    content_type = Committee

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if len(errors) and any([
                True for error in errors
                if error.message == u'error_default_template_is_in_allowed_templates']):
            self.widgets['allowed_ad_hoc_agenda_item_templates'].error = True
            self.widgets['ad_hoc_template'].error = True

        return super(EditForm, self).handleApply(self, action)
