from datetime import datetime
from DateTime import DateTime
from opengever.base import _
from opengever.base.date_time import as_utc
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.annotation import IAnnotations
from zope.component.hooks import getSite
from zope.interface import Interface, alsoProvides


class IChanged(model.Schema):
    """ IChanged contains the changed field tracking
    when an object was last changed by a user.
    """

    form.omitted('changed')
    changed = schema.Datetime(
        title=_(u'changed_date',
                default="Date last changed"),
        required=False,
        readonly=True,
    )


alsoProvides(IChanged, IFormFieldProvider)


class IChangedMarker(Interface):
    pass


class Changed(object):

    def __init__(self, context):
        self.context = context

    def _get_changed(self):
        # XXX Can be deleted once the changed metadata has been filled on all deployments
        # https://github.com/4teamwork/opengever.core/issues/4988
        if self.context.changed is None:
            return as_utc(self.context.modified().asdatetime())
        return self.context.changed

    def _set_changed(self, value):
        # Make sure we have a python datetime
        if isinstance(value, DateTime):
            value = value.asdatetime()
        assert isinstance(value, datetime), "changed should be a python datetime"
        # Make sure we have a timezone aware datetime
        assert value.tzinfo is not None, "changed should be timezone aware"

        # Make sure we save the datetime as utc. This is especially important
        # to avoid the unpickling issues when unpickling a datetime obtained
        # from DateTime.asdatetime()
        self.context.changed = as_utc(value)

    changed = property(_get_changed, _set_changed)


# XXX Can be deleted once the changed metadata has been filled on all deployments
# https://github.com/4teamwork/opengever.core/issues/4988
METADATA_CHANGED_FILLED_KEY = 'opengever.base.behaviors.changed.filled'


def has_metadata_changed_been_filled():
    site = getSite()
    annotations = IAnnotations(site)
    if METADATA_CHANGED_FILLED_KEY not in annotations:
        # This is a newly setup deployment or one where the first upgrade has not been run.
        return True
    return bool(annotations.get(METADATA_CHANGED_FILLED_KEY))
