from plone.dexterity.content import Container
from plone.supermodel import model


class IPeriod(model.Schema):
    """Marker interface for period."""


class Period(Container):
    pass
