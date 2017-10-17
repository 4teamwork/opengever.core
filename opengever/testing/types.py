from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface


class IDummySchema(model.Schema):
    """Dummy schema used for testing.
    """

    int_field = schema.Int(
        title=u'Int Field',
        required=False,
        default=111,
    )


class IDummyWithMarkerSchema(model.Schema):
    """Dummy schema used for testing.
    """

    int_marker_field = schema.Int(
        title=u'Behavior (with marker) Int Field',
        required=False,
        default=111,
    )

alsoProvides(IDummyWithMarkerSchema, IFormFieldProvider)


class IDummyAttributeStorageBehavior(model.Schema):

    attr_behavior_int_field = schema.Int(
        title=u'Behavior (AttributeStorage) Int Field',
        required=False,
        default=222,
    )

alsoProvides(IDummyAttributeStorageBehavior, IFormFieldProvider)


class IDummyAnnotationStorageBehavior(model.Schema):

    ann_behavior_int_field = schema.Int(
        title=u'Behavior (AnnotationStorage) Int Field',
        required=False,
        default=333,
    )

alsoProvides(IDummyAnnotationStorageBehavior, IFormFieldProvider)


class Dummy(Container):
    """Dummy type used for testing"""


class IDummyMarker(Interface):
    """Behavior marker interface"""
