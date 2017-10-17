from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base import _
from opengever.base.acquisition import acquired_default_factory
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from opengever.base.restricted_vocab import propagate_vocab_restrictions
from opengever.base.restricted_vocab import RestrictedVocabularyFactory
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from plone.autoform.directives import write_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


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

    write_permission(date_of_cassation='opengever.base.EditDateOfCassation')
    form.widget(date_of_cassation=DatePickerFieldWidget)
    date_of_cassation = schema.Date(
        title=_(u'label_dateofcassation', default=u'Date of cassation'),
        required=False,
    )

    write_permission(date_of_submission='opengever.base.EditDateOfSubmission')
    form.widget(date_of_submission=DatePickerFieldWidget)
    date_of_submission = schema.Date(
        title=_(u'label_dateofsubmission', default=u'Date of submission'),
        required=False,
    )


alsoProvides(ILifeCycle, IFormFieldProvider)


def propagate_vocab_restrictions_to_children(container, event):
    if ILocalrolesModifiedEvent.providedBy(event):
        return

    restricted_fields = [
        ILifeCycle['retention_period'],
        ILifeCycle['archival_value'],
        ILifeCycle['custody_period']]

    propagate_vocab_restrictions(
        container, event, restricted_fields, ILifeCycleMarker)


# ---------- RETENTION PERIOD -----------
# Vocabulary
def _get_retention_period_choices():
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IRetentionPeriodRegister)
    choices = []
    nums = getattr(proxy, 'retention_period')

    for i, num in enumerate(nums):
        num = int(num)
        pos = int(nums[- i - 1])
        choices.append((pos, num))

    return choices


def _is_retention_period_restricted():
    registry = getUtility(IRegistry)
    retention_period_settings = registry.forInterface(IRetentionPeriodRegister)
    return retention_period_settings.is_restricted


retention_period_vf = RestrictedVocabularyFactory(
    ILifeCycle['retention_period'],
    _get_retention_period_choices,
    message_factory=_,
    restricted=_is_retention_period_restricted)


@provider(IContextAwareDefaultFactory)
def retention_period_default(context):
    default_factory = acquired_default_factory(
        field=ILifeCycle['retention_period'],
        default=5)
    return default_factory(context)

ILifeCycle['retention_period'].defaultFactory = retention_period_default


# ---------- CUSTODY PERIOD -----------
# Vocabulary

def _get_custody_period_choices():
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IBaseCustodyPeriods)
    choices = []
    nums = getattr(proxy, 'custody_periods')

    for num in nums:
        num = int(num)
        choices.append((num, num))

    return choices


custody_period_vf = RestrictedVocabularyFactory(
    ILifeCycle['custody_period'],
    _get_custody_period_choices,
    message_factory=_,
    restricted=True)


@provider(IContextAwareDefaultFactory)
def custody_period_default(context):
    default_factory = acquired_default_factory(
        field=ILifeCycle['custody_period'],
        default=30)
    return default_factory(context)

ILifeCycle['custody_period'].defaultFactory = custody_period_default


# ARCHIVAL VALUE: Vocabulary and default value
ARCHIVAL_VALUE_UNCHECKED = u'unchecked'
ARCHIVAL_VALUE_PROMPT = u'prompt'
ARCHIVAL_VALUE_WORTHY = u'archival worthy'
ARCHIVAL_VALUE_UNWORTHY = u'not archival worthy'
ARCHIVAL_VALUE_SAMPLING = u'archival worthy with sampling'
ARCHIVAL_VALUE_CHOICES = (
    (1, ARCHIVAL_VALUE_UNCHECKED),
    (2, ARCHIVAL_VALUE_PROMPT),
    (3, ARCHIVAL_VALUE_WORTHY),
    (3, ARCHIVAL_VALUE_UNWORTHY),
    (3, ARCHIVAL_VALUE_SAMPLING),
)


archival_value_vf = RestrictedVocabularyFactory(
    ILifeCycle['archival_value'],
    ARCHIVAL_VALUE_CHOICES,
    message_factory=_,
    restricted=True)


@provider(IContextAwareDefaultFactory)
def archival_value_default(context):
    default_factory = acquired_default_factory(
        field=ILifeCycle['archival_value'],
        default=ARCHIVAL_VALUE_UNCHECKED)
    return default_factory(context)

ILifeCycle['archival_value'].defaultFactory = archival_value_default
