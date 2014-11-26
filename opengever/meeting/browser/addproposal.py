from five import grok
from opengever.globalindex.oguid import Oguid
from opengever.meeting.model.proposal import IProposalModel
from opengever.meeting.model.proposal import Proposal
from opengever.ogds.base.utils import create_session
from plone.directives import dexterity
from z3c.form import field
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class AddForm(dexterity.AddForm):
    grok.name('opengever.meeting.proposal')

    fields = field.Fields(IProposalModel)

    def create_model(self, obj, data):
        session = create_session()
        oguid = Oguid.for_object(obj)
        session.add(Proposal(oguid=oguid, **data))

        # for event handling to work, the object must be acquisition-wrapped
        notify(ObjectModifiedEvent(obj.__of__(self.context)))

    def createAndAdd(self, data):
        """Create proposal, this is a two-step process:

            1) Create the plone proxoy object (with no data)
            2) Create database model where the data is stored

        """
        obj = super(AddForm, self).createAndAdd(data={})
        self.create_model(obj, data)
        return obj
