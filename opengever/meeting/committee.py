from opengever.base.oguid import Oguid
from opengever.core.model import create_session
from opengever.meeting import _
from opengever.meeting.model import Committee as CommitteeModel
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent


class ICommittee(form.Schema):
    """Base schema for the committee.
    """


class ICommitteeModel(Interface):
    """Proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
        max_length=256,
        )


class Committee(Container):
    """Plone Proxy for a Committe."""

    model_schema = ICommitteeModel

    @classmethod
    def partition_data(cls, data):
        """Partition input data in model data and plone object data.

        Currenctly plone object data is empty.
        """
        obj_data = {}
        return obj_data, data

    def create_model(self, data, context):
        session = create_session()
        oguid = Oguid.for_object(self)

        aq_wrapped_self = self.__of__(context)
        session.add(CommitteeModel(oguid=oguid, **data))

        # for event handling to work, the object must be acquisition-wrapped
        notify(ObjectModifiedEvent(aq_wrapped_self))

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return CommitteeModel.query.get_by_oguid(oguid)
