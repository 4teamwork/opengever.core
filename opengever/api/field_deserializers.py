# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.schema import IUTCDatetime
from persistent.interfaces import IPersistent
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DatetimeFieldDeserializer
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from pytz import utc
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IField
import dateutil


@implementer(IFieldDeserializer)
@adapter(IField, IPersistent, IBrowserRequest)
class PersistentDefaultFieldDeserializer(DefaultFieldDeserializer):
    """Default field deserializer for persisten objects"""


@implementer(IFieldDeserializer)
@adapter(IDatetime, IPersistent, IBrowserRequest)
class PersistentDatetimeFieldDeserializer(DatetimeFieldDeserializer):
    """Datetime field deserializer for persisten objects"""


@implementer(IFieldDeserializer)
@adapter(IDate, IDexterityContent, IOpengeverBaseLayer)
class DateFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        value = super(DateFieldDeserializer, self).__call__(value)
        reject_year_before_1900(value)
        return value


@implementer(IFieldDeserializer)
@adapter(IDatetime, IDexterityContent, IOpengeverBaseLayer)
class DatetimeFieldDeserializer(DatetimeFieldDeserializer):
    def __call__(self, value):
        value = super(DatetimeFieldDeserializer, self).__call__(value)
        reject_year_before_1900(value)
        return value


@implementer(IFieldDeserializer)
@adapter(IUTCDatetime, IDexterityContent, IBrowserRequest)
class UTCDatetimeFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        # Inspired from DatetimeFieldDeserializer, but we always save the value
        # as timezone aware in UTC and reject years before 1900.

        # This happens when a 'null' is posted for a non-required field.
        if value is None:
            self.field.validate(value)
            return

        # Parse ISO 8601 string with dateutil
        try:
            dt = dateutil.parser.parse(value)
        except ValueError:
            raise ValueError(u"Invalid date: {}".format(value))

        # Convert to TZ aware in UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(utc)
        else:
            dt = utc.localize(dt)

        self.field.validate(dt)
        reject_year_before_1900(dt)
        return dt


def reject_year_before_1900(value):
    """Because strftime() methods don't support years before 1900, we can't
    represent them. We therefore reject them here.
    """
    if isinstance(value, (date, datetime)) and value.year < 1900:
        raise ValueError(
            'year=%s is invalid. Year must be >= 1900.' % value.year)
