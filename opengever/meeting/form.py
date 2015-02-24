from opengever.base.model import create_session
from opengever.base.utils import disable_edit_bar
from opengever.meeting import _
from opengever.meeting import is_meeting_feature_enabled
from plone.autoform.form import AutoExtensibleForm
from z3c.form import button
from z3c.form.form import AddForm
from z3c.form.form import EditForm
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
        return self.model_class(**data)

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

    @button.buttonAndHandler(_(u'Cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.cancelURL())

    def nextURL(self):
        return self.context.absolute_url()

    def cancelURL(self):
        return self.context.absolute_url()


class ModelEditForm(EditForm):
    """Base edit-form for stand-alone model objects.
    """

    ignoreContext = True
    is_model_view = True
    is_model_edit_view = True

    fields = None
    field_prefix = 'form.widgets.'

    def __init__(self, context, request, model):
        super(ModelEditForm, self).__init__(context, request)
        self.model = model
        self._has_finished_edit = False

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        values = self.model.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            self.request[self.field_prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(ModelEditForm, self).updateWidgets()

    def applyChanges(self, data):
        self.model.update_model(data)
        # pretend to always change the underlying data
        self._has_finished_edit = True
        return True

    # this renames the button but otherwise preserves super's behavior
    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        # self as first argument is required by the decorator
        super(ModelEditForm, self).handleApply(self, action)

    @button.buttonAndHandler(_(u'Cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        raise NotImplementedError()

    def render(self):
        if self._has_finished_edit:
            return self.request.response.redirect(self.nextURL())
        return super(ModelEditForm, self).render()


class ModelProxyAddForm(object):
    """Base add-form for dexterity proxy objects and their associated model.
    """

    content_type = None
    fields = None

    def render(self):
        assert self.fields, 'must specify model fields to render!'
        assert self.content_type, 'must configure content type!'

        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(ModelProxyAddForm, self).render()

    def createAndAdd(self, data):
        """Create sql-model supported content types.

        This is a two-step process and involves two schema interfaces:
            1) Create the plone proxy object (with plone schema data)
            2) Create database model and store the model schema data

        """
        obj_data, model_data = self.content_type.partition_data(data)
        obj = super(ModelProxyAddForm, self).createAndAdd(data=obj_data)
        obj.create_model(model_data, self.context)
        return obj


class ModelProxyEditForm(object):
    """Base edit-form for dexterity proxy objects and their associated model.
    """

    content_type = None
    fields = None

    def render(self):
        assert self.fields, 'must specify model fields to render!'
        assert self.content_type, 'must configure content type!'

        if not is_meeting_feature_enabled():
            raise Unauthorized

        if not self.context.is_editable():
            raise Unauthorized

        return super(ModelProxyEditForm, self).render()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        values = self.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            self.request[prefix + fieldname] = value

    def get_edit_values(self, keys):
        return self.context.get_edit_values(keys)

    def updateWidgets(self):
        self.inject_initial_data()
        super(ModelProxyEditForm, self).updateWidgets()

    def partition_data(self, data):
        obj_data, model_data = self.content_type.partition_data(data)
        return obj_data, model_data

    def update_model(self, model_data):
        self.context.update_model(model_data)

    def applyChanges(self, data):
        obj_data, model_data = self.partition_data(data)
        self.update_model(model_data)
        super(ModelProxyEditForm, self).applyChanges(obj_data)
        # pretend to always change the underlying data
        return True
