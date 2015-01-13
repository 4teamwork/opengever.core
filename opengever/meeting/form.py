from opengever.meeting import is_meeting_feature_enabled
from zExceptions import Unauthorized


class MeetingModelAddForm(object):

    content_type = None
    fields = None

    def render(self):
        assert self.fields, 'must specify model fields to render!'
        assert self.content_type, 'must configure content type!'

        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(MeetingModelAddForm, self).render()

    def createAndAdd(self, data):
        """Create sql-model supported content types.

        This is a two-step process and involves two schema interfaces:
            1) Create the plone proxy object (with plone schema data)
            2) Create database model and store the model schema data

        """
        obj_data, model_data = self.content_type.partition_data(data)
        obj = super(MeetingModelAddForm, self).createAndAdd(data=obj_data)
        obj.create_model(model_data, self.context)
        return obj


class MeetingModelEditForm(object):

    content_type = None
    fields = None

    def render(self):
        assert self.fields, 'must specify model fields to render!'
        assert self.content_type, 'must configure content type!'

        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(MeetingModelEditForm, self).render()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        values = self.context.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            self.request[prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(MeetingModelEditForm, self).updateWidgets()

    def applyChanges(self, data):
        obj_data, model_data = self.content_type.partition_data(data)
        self.context.update_model(model_data)
        super(MeetingModelEditForm, self).applyChanges(obj_data)
        # pretend to always change the underlying data
        return True
