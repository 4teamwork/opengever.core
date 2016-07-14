from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base import _
from opengever.base.behaviors import utils
from opengever.base.behaviors.utils import create_restricted_vocabulary
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class ILifeCycleMarker(Interface):
    pass


class ILifeCycle(form.Schema):

    form.fieldset(
        u'lifecycle',
        label=_(u'fieldset_lifecycle', default=u'Life Cycle'),
        fields=[
            u'retention_period',
            u'retention_period_annotation',
            u'archival_value',
            u'archival_value_annotation',
            u'custody_period',
            u'date_of_cassation',
            u'date_of_submission', ],
    )

    #dexterity.write_permission(retention_period='cmf.ManagePortal')
    retention_period = schema.Choice(
        title=_(u'label_retention_period', u'Retention period (years)'),
        description=_(u'help_retention_period', default=u''),
        source=u'lifecycle_retention_period_vocabulary',
        required=True,
    )

    #dexterity.write_permission(retention_period_annotation='cmf.ManagePortal')
    retention_period_annotation = schema.Text(
        title=_(u'label_retention_period_annotation',
                default=u'retentionPeriodAnnotation'),
        required=False
    )

    #dexterity.write_permission(archival_value='cmf.ManagePortal')
    archival_value = schema.Choice(
        title=_(u'label_archival_value', default=u'Archival value'),
        description=_(u'help_archival_value', default=u'Archival value code'),
        source=u'lifecycle_archival_value_vocabulary',
        required=True,
    )

    #dexterity.write_permission(archival_value_annotation='cmf.ManagePortal')
    archival_value_annotation = schema.Text(
        title=_(u'label_archival_value_annotation',
                default=u'archivalValueAnnotation'),
        required=False
    )

    #dexterity.write_permission(custody_period='cmf.ManagePortal')
    custody_period = schema.Choice(
        title=_(u'label_custody_period', default=u'Custody period (years)'),
        description=_(u'help_custody_period', default=u''),
        source=u'lifecycle_custody_period_vocabulary',
        required=True,
    )

    #dexterity.write_permission(date_of_cassation='cmf.ManagePortal')
    form.widget(date_of_cassation=DatePickerFieldWidget)
    date_of_cassation = schema.Date(
        title=_(u'label_dateofcassation', default=u'Date of cassation'),
        required=False,
    )

    #dexterity.write_permission(date_of_submission='cmf.ManagePortal')
    form.widget(date_of_submission=DatePickerFieldWidget)
    date_of_submission = schema.Date(
        title=_(u'label_dateofsubmission', default=u'Date of submission'),
        required=False,
    )


alsoProvides(ILifeCycle, IFormFieldProvider)


@grok.subscribe(ILifeCycleMarker, IObjectModifiedEvent)
def validate_children(folder, event):
    aq_fields = [ILifeCycle['retention_period'],
                 ILifeCycle['archival_value'],
                 ILifeCycle['custody_period']]

    utils.overrides_child(folder, event, aq_fields, ILifeCycleMarker)


# ---------- RETENTION PERIOD -----------
# Vocabulary
def _get_retention_period_options(vocabulary):
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IRetentionPeriodRegister)
    options = []
    nums = getattr(proxy, 'retention_period')

    for i, num in enumerate(nums):
        num = int(num)
        pos = int(nums[- i - 1])
        options.append((pos, num))

    return options


def _is_retention_period_restricted(*args, **kwargs):
    registry = getUtility(IRegistry)
    retention_period_settings = registry.forInterface(IRetentionPeriodRegister)
    return retention_period_settings.is_restricted


# TODO: This will be rewritten to eliminate one level of factories
retention_period_vf_factory = create_restricted_vocabulary(
    ILifeCycle['retention_period'],
    _get_retention_period_options,
    message_factory=_,
    restricted=_is_retention_period_restricted)


# Default value
# XXX: Eventually rewrite this as a context aware defaultFactory
form.default_value(field=ILifeCycle['retention_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['retention_period'],
        default=5))


# ---------- CUSTODY PERIOD -----------
# Vocabulary

def _get_custody_period_options(context):
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IBaseCustodyPeriods)
    options = []
    nums = getattr(proxy, 'custody_periods')

    for num in nums:
        num = int(num)
        options.append((num, num))

    return options


# TODO: This will be rewritten to eliminate one level of factories
custody_period_vf_factory = create_restricted_vocabulary(
    ILifeCycle['custody_period'],
    _get_custody_period_options,
    message_factory=_,
    restricted=lambda self: True)


# Default value
# XXX: Eventually rewrite this as a context aware defaultFactory
form.default_value(field=ILifeCycle['custody_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['custody_period'],
        default=30,
    )
)


# ARCHIVAL VALUE: Vocabulary and default value
ARCHIVAL_VALUE_UNCHECKED = u'unchecked'
ARCHIVAL_VALUE_PROMPT = u'prompt'
ARCHIVAL_VALUE_WORTHY = u'archival worthy'
ARCHIVAL_VALUE_UNWORTHY = u'not archival worthy'
ARCHIVAL_VALUE_SAMPLING = u'archival worthy with sampling'
ARCHIVAL_VALUE_OPTIONS = (
    (1, ARCHIVAL_VALUE_UNCHECKED),
    (2, ARCHIVAL_VALUE_PROMPT),
    (3, ARCHIVAL_VALUE_WORTHY),
    (3, ARCHIVAL_VALUE_UNWORTHY),
    (3, ARCHIVAL_VALUE_SAMPLING),
)


# TODO: This will be rewritten to eliminate one level of factories
archival_value_vf_factory = create_restricted_vocabulary(
    ILifeCycle['archival_value'],
    ARCHIVAL_VALUE_OPTIONS,
    message_factory=_,
    restricted=lambda self: True)


# XXX: Eventually rewrite this as a context aware defaultFactory
form.default_value(field=ILifeCycle['archival_value'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['archival_value'],
        default=ARCHIVAL_VALUE_UNCHECKED
    )
)
