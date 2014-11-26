from plone.dexterity.content import Container
from plone.directives import form
from zope.interface import implements


class IProposal(form.Schema):
    """Proposal Schema Interface"""


class Proposal(Container):
    implements(IProposal)
