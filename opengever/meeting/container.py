from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from plone.dexterity.content import Container
from z3c.form import interfaces
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class ModelContainer(Container):

    model_class = None
    model_schema = None
    content_schema = None

    @classmethod
    def partition_data(cls, data):
        """Partition input data in model data and plone object data.

        """
        obj_data = {}
        for field_name in cls.content_schema.names(all=True):
            if field_name in data:
                obj_data[field_name] = data.pop(field_name)

        return obj_data, data

    def get_edit_values(self, fieldnames):
        values = {}
        model = self.load_model()
        for fieldname in fieldnames:
            value = getattr(model, fieldname, None)
            if value is None:
                continue
            values[fieldname] = value
        return values

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return self.model_class.query.get_by_oguid(oguid)

    def create_model(self, data, context):
        session = create_session()
        oguid = Oguid.for_object(self)

        # some plone-integration relies on acquisition, thus we need to wrap
        # the just created plone content now.
        aq_wrapped_self = self.__of__(context)
        self.update_model_create_arguments(data, context)
        model_instance = self.model_class(oguid=oguid, **data)
        session.add(model_instance)
        session.flush()  # required to create an autoincremented id
        self._after_model_created(model_instance)

        notify(ObjectModifiedEvent(aq_wrapped_self))

    def _after_model_created(self, model_instance):
        """Hook called right after creating a model instance."""
        pass

    def update_model(self, data):
        """Store form input in relational database.

        KISS: Currently assumes that each input is a change and thus always
        fires a changed event.

        """
        model = self.load_model()
        for key, value in data.items():
            if value is interfaces.NOT_CHANGED:
                continue
            setattr(model, key, value)

        notify(ObjectModifiedEvent(self))
        return True

    def update_model_create_arguments(self, data, context):
        return data
