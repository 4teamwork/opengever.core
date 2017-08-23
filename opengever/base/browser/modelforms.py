from opengever.base import _
from opengever.base.model import create_session
from opengever.base.utils import disable_edit_bar
from plone import api
from plone.autoform.form import AutoExtensibleForm
from z3c.form import button
from z3c.form.form import AddForm
from z3c.form.form import EditForm
from z3c.form.interfaces import IDataConverter
from zExceptions import Unauthorized


class ModelAddForm(AutoExtensibleForm, AddForm):
    """Base add-form for stand-alone model objects.
    """

    ignoreContext = True
    schema = None
    model_class = None

    def __init__(self, context, request):
        super(ModelAddForm, self).__init__(context, request)
        self._created_object = None
        disable_edit_bar()

    def create(self, data):
        self.validate(data)
        return self.model_class(**data)

    def validate(self, data):
        """Hook to perform additional input validation."""
        pass

    def add(self, obj):
        session = create_session()
        session.add(obj)
        session.flush()  # required to create an autoincremented id
        self._created_object = obj

    # this renames the button but otherwise preserves super's behavior
    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleAdd(self, action):
        # self as first argument is required by the decorator
        super(ModelAddForm, self).handleAdd(self, action)
        if not self._finishedAdd:
            return

        api.portal.show_message(
            _(u'message_record_created', default='Record created'),
            api.portal.get().REQUEST)
        return self.request.RESPONSE.redirect(self.nextURL())

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.cancelURL())

    def nextURL(self):
        return self.context.absolute_url()

    def cancelURL(self):
        return self.context.absolute_url()


class ModelEditForm(AutoExtensibleForm, EditForm):
    """Base edit-form for stand-alone model objects.
    """

    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX
    schema = None

    field_prefix = 'form.widgets.'

    def __init__(self, context, request, model):
        super(ModelEditForm, self).__init__(context, request)
        self.model = model

    def __call__(self):
        if not self.model.is_editable():
            raise Unauthorized('Editing is not allowed')

        return super(ModelEditForm, self).__call__()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        values = self.model.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            widget = self.widgets[fieldname]
            value = IDataConverter(widget).toWidgetValue(value)
            widget.value = value

    def updateWidgets(self):
        super(ModelEditForm, self).updateWidgets()
        self.inject_initial_data()
        # inject_initial_data will change widget values, they might need
        # another update
        self.widgets.update()

    def applyChanges(self, data):
        self.model.update_model(data)

    def validate(self, data):
        return

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.validate(data)

        self.applyChanges(data)
        self.status = self.successMessage

        api.portal.show_message(
            _(u'message_changes_saved', default='Changes saved'),
            api.portal.get().REQUEST)

        return self.redirect_to_next_url()

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        raise NotImplementedError()

    def redirect_to_next_url(self):
        return self.request.RESPONSE.redirect(self.nextURL())
