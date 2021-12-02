from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base import _
from opengever.base.acquisition import acquired_default_factory
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister
from opengever.base.restricted_vocab import RestrictedVocabularyFactory
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ILifeCycleMarker(Interface):
    pass


class ILifeCycle(model.Schema):

    model.fieldset(
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

    form.write_permission(retention_period='opengever.base.EditLifecycleAndClassification')
    retention_period = schema.Choice(
        title=_(u'label_retention_period', u'Retention period (years)'),
        description=_(u'help_retention_period', default=u''),
        source=u'lifecycle_retention_period_vocabulary',
        required=True,
    )

    form.write_permission(retention_period_annotation='opengever.base.EditLifecycleAndClassification')
    retention_period_annotation = schema.Text(
        title=_(u'label_retention_period_annotation',
                default=u'retentionPeriodAnnotation'),
        required=False
    )

    form.write_permission(archival_value='opengever.base.EditLifecycleAndClassification')
    archival_value = schema.Choice(
        title=_(u'label_archival_value', default=u'Archival value'),
        description=_(u'help_archival_value', default=u'Archival value code'),
        source=u'lifecycle_archival_value_vocabulary',
        required=True,
    )

    form.write_permission(archival_value_annotation='opengever.base.EditLifecycleAndClassification')
    archival_value_annotation = schema.Text(
        title=_(u'label_archival_value_annotation',
                default=u'archivalValueAnnotation'),
        required=False
    )

    form.write_permission(custody_period='opengever.base.EditLifecycleAndClassification')
    custody_period = schema.Choice(
        title=_(u'label_custody_period', default=u'Custody period (years)'),
        description=_(u'help_custody_period', default=u''),
        source=u'lifecycle_custody_period_vocabulary',
        required=True,
    )

    form.write_permission(date_of_cassation='cmf.ManagePortal')
    form.read_permission(date_of_cassation='cmf.ManagePortal')
    form.widget(date_of_cassation=DatePickerFieldWidget)
    date_of_cassation = schema.Date(
        title=_(u'label_dateofcassation', default=u'Date of cassation'),
        required=False,
    )

    form.write_permission(date_of_submission='opengever.base.EditDateOfSubmission')
    form.widget(date_of_submission=DatePickerFieldWidget)
    date_of_submission = schema.Date(
        title=_(u'label_dateofsubmission', default=u'Date of submission'),
        required=False,
    )


alsoProvides(ILifeCycle, IFormFieldProvider)


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


@implementer(IVocabularyFactory)
class CustodyPeriodVocabulary(object):

    def __call__(self, context):
        terms = []
        custody_periods = getUtility(IRegistry).forInterface(IBaseCustodyPeriods).custody_periods
        for custody_period in custody_periods:
            custody_period = int(custody_period)
            terms.append(SimpleTerm(custody_period, title=_(custody_period)))

        return SimpleVocabulary(terms)


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
ARCHIVAL_VALUE_CHOICES = [
    ARCHIVAL_VALUE_UNCHECKED,
    ARCHIVAL_VALUE_PROMPT,
    ARCHIVAL_VALUE_WORTHY,
    ARCHIVAL_VALUE_UNWORTHY,
    ARCHIVAL_VALUE_SAMPLING,
]


@implementer(IVocabularyFactory)
class ArchivalValueVocabulary(object):

    def __call__(self, context):
        terms = []
        for archival_value in ARCHIVAL_VALUE_CHOICES:
            terms.append(
                SimpleTerm(value=archival_value, token=archival_value,
                           title=_(archival_value)))

        return SimpleVocabulary(terms)


@provider(IContextAwareDefaultFactory)
def archival_value_default(context):
    default_factory = acquired_default_factory(
        field=ILifeCycle['archival_value'],
        default=ARCHIVAL_VALUE_UNCHECKED)
    return default_factory(context)


ILifeCycle['archival_value'].defaultFactory = archival_value_default
