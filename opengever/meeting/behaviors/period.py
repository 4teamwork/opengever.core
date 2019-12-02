from collective import dexteritytextindexer
from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base import _ as bmf
from opengever.meeting import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


def current_year():
    return unicode(date.today().year)


def first_day_of_current_year():
    return date(date.today().year, 1, 1)


def last_day_of_current_year():
    return date(date.today().year, 12, 31)


class IPeriodSchema(model.Schema):
    """Base schema for period."""

    model.fieldset(
        u'common',
        label=bmf(u'fieldset_common', default=u'Common'),
        fields=[
            u'title',
            u'start',
            u'end',
            u'decision_sequence_number',
            u'meeting_sequence_number',
        ],
    )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=True,
        max_length=256,
        defaultFactory=current_year,
    )

    form.widget(start=DatePickerFieldWidget)
    start = schema.Date(
        title=_('label_date_from', default='Start date'),
        required=True,
        defaultFactory=first_day_of_current_year,
    )

    form.widget(end=DatePickerFieldWidget)
    end = schema.Date(
        title=_('label_date_to', default='End date'),
        required=True,
        defaultFactory=last_day_of_current_year,
    )

    form.write_permission(decision_sequence_number='cmf.ManagePortal')
    decision_sequence_number = schema.Int(
        title=_(u'label_decision_sequence_number',
                default=u'Sequence number for decisions'),
        description=_(u'description_decision_sequence_number',
                     default=u'Only visible for managers. Only change this if '
                              'you know what you are doing!'),
        required=True,
        default=0,
    )

    form.write_permission(meeting_sequence_number='cmf.ManagePortal')
    meeting_sequence_number = schema.Int(
        title=_(u'label_meeting_sequence_number',
                default=u'Sequence number for meetings'),
        description=_(u'description_meeting_sequence_number',
                     default=u'Only visible for managers. Only change this if '
                              'you know what you are doing!'),
        required=True,
        default=0,
    )


alsoProvides(IPeriodSchema, IFormFieldProvider)
