from opengever.meeting import is_meeting_feature_enabled
from zExceptions import Unauthorized


class MeetingModelAddForm(object):

    content_type = None

    def render(self):
        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(MeetingModelAddForm, self).render()

    def create_model(self, obj, data):
        obj.create_model(data, self.context)

    def createAndAdd(self, data):
        """Create sql-model supported content types.

        This is a two-step process and involves two schema interfaces:
            1) Create the plone proxy object (with plone schema data)
            2) Create database model and store the model schema data

        """
        obj_data, model_data = self.content_type.partition_data(data)
        obj = super(MeetingModelAddForm, self).createAndAdd(data=obj_data)
        self.create_model(obj, model_data)
        return obj
