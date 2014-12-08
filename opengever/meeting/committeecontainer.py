from plone.dexterity.content import Container
from plone.directives import form


class ICommitteeContainer(form.Schema):
    """Base schema for a the committee container.
    """


class CommitteeContainer(Container):
    """Committee Container class, a container for all committeees."""
