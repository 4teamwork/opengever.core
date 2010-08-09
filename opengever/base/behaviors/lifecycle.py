from zope import schema
from zope.interface import alsoProvides, Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import zope.component
from z3c.form import validator

from five import grok

from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot

from opengever.base import _
from opengever.base.behaviors import utils

from plone.registry.interfaces import IRegistry
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister


class ILifeCycleMarker(Interface):
    pass



class ILifeCycle(form.Schema):

    form.fieldset(
        u'lifecycle',
        label = _(u'fieldset_lifecycle', default=u'Life Cycle'),
        fields = [
            u'retention_period',
            u'retention_period_annotation',
            u'archival_value',    
            u'archival_value_annotation',
            u'custody_period',
            ],
        )

    retention_period = schema.Choice(
        title = _(u'label_retention_period', u'Retention period (years)'),
        description = _(u'help_retention_period', default=u''),
        source = u'lifecycle_retention_period_vocabulary',
        required = True,
        )

    retention_period_annotation = schema.Text(
        title=_(u'label_retention_period_annotation', default=u'retentionPeriodAnnotation'),
        description = _(u'help_retention_period_annotation', default=u''),
        required=False
        )

    archival_value = schema.Choice(
        title = _(u'label_archival_value', default=u'Archival value'),
        description = _(u'help_archival_value', default=u'Archival value code'),
        source = u'lifecycle_archival_value_vocabulary',
        required = True,
        )

    archival_value_annotation = schema.Text(
        title=_(u'label_archival_value_annotation', default=u'archivalValueAnnotation'),
        description = _(u'help_archival_value_annotation', default=u''),
        required=False
        )

    custody_period = schema.Choice(
        title = _(u'label_custody_period', default=u'Custody period (years)'),
        description = _(u'help_custody_period', default=u''),
        source = u'lifecycle_custody_period_vocabulary',
        required = True,
        )


alsoProvides(ILifeCycle, IFormFieldProvider)

@grok.subscribe(ILifeCycleMarker, IObjectModifiedEvent)
def validate_children(folder, event):
    aq_fields = [ILifeCycle['retention_period'], ILifeCycle['archival_value'], ILifeCycle['custody_period']]

    utils.overrides_child(folder, event, aq_fields, ILifeCycleMarker)

# CUSTODY PERIOD / RETENTION PERIOD

class IntLowerEqualThanParentValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(IntLowerEqualThanParentValidator, self).validate(value)
        # should not be negative
        if int(value)<0:
            raise schema.interfaces.TooSmall()
        # get parent value
        #XXX CHANGED FROM PATH_TRANSLATED TO PATH_INFO because the test don't work
        if '++add++' in self.request.get('PATH_INFO', object()):
            obj = self.context
        else:
            obj = self.context.aq_inner.aq_parent
        parent_value = -1
        while parent_value<0 and not ISiteRoot.providedBy(obj):
            cf_obj = zope.component.queryAdapter(obj, ILifeCycle)
            if cf_obj:
                try:
                    parent_value = int(self.field.get(cf_obj))
                except AttributeError:
                    pass
                except TypeError:
                    parent_value = 0
            try:
                obj = obj.aq_inner.aq_parent
            except AttributeError:
                return
        # should not be bigger than parent
        if parent_value>-1 and int(value)>parent_value:
            raise schema.interfaces.TooBig()


# ---------- RETENTION PERIOD -----------
# Vocabulary
def _get_retention_period_options(vocabulary):
    registry = zope.component.getUtility(IRegistry)
    proxy = registry.forInterface(IRetentionPeriodRegister)
    options = []
    nums = getattr(proxy, 'retention_period')
    for i, num in enumerate(nums):
        num = int(num)
        pos = int(nums[-i-1])
        options.append((pos, num))
    return options
grok.global_utility(utils.create_restricted_vocabulary(
        ILifeCycle['retention_period'],
        _get_retention_period_options,
        message_factory=_),
                    provides=schema.interfaces.IVocabularyFactory,
                    name=u'lifecycle_retention_period_vocabulary')

# Default value
form.default_value(field=ILifeCycle['retention_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['retention_period'],
        default=5,
        )
    )

# Validator
class CustodyPeriodValidator(IntLowerEqualThanParentValidator):
    pass
validator.WidgetValidatorDiscriminators(
    CustodyPeriodValidator,
    field=ILifeCycle['custody_period']
    )

zope.component.provideAdapter(CustodyPeriodValidator)


# ---------- CUSTODY PERIOD -----------
# Vocabulary
def _get_custody_period_options(context):
    registry = zope.component.getUtility(IRegistry)
    proxy = registry.forInterface(IBaseCustodyPeriods)
    options = []
    nums = getattr(proxy, 'custody_periods')
    for i, num in enumerate(nums):
        num = int(num)
        pos = int(nums[-i-1])
        options.append((pos, num))
    return options
grok.global_utility(utils.create_restricted_vocabulary(
        ILifeCycle['custody_period'],
        _get_custody_period_options,
        message_factory=_),
                    provides=schema.interfaces.IVocabularyFactory,
                    name=u'lifecycle_custody_period_vocabulary')

# Default value
form.default_value(field=ILifeCycle['custody_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['custody_period'],
        default=10,
        )
    )

# Validator
class RetentionPeriodValidator(IntLowerEqualThanParentValidator):
    pass
validator.WidgetValidatorDiscriminators(
    RetentionPeriodValidator,
    field=ILifeCycle['retention_period']
    )
zope.component.provideAdapter(RetentionPeriodValidator)



# ARCHIVAL VALUE: Vocabulary and default value
ARCHIVAL_VALUE_UNCHECKED = u'archival_value : unchecked'
ARCHIVAL_VALUE_PROMPT = u'archival_value : prompt'
ARCHIVAL_VALUE_WORTHY = u'archival_value : archival worthy'
ARCHIVAL_VALUE_UNWORTHY = u'archival_value : not archival worthy'
ARCHIVAL_VALUE_SAMPLING  = u'archival_value : archival worthy with sampling'
ARCHIVAL_VALUE_OPTIONS = (
    (1,         ARCHIVAL_VALUE_UNCHECKED),
    (2,         ARCHIVAL_VALUE_PROMPT),
    (3,         ARCHIVAL_VALUE_WORTHY),
    (3,         ARCHIVAL_VALUE_UNWORTHY),
    (3,         ARCHIVAL_VALUE_SAMPLING ),
    )
grok.global_utility(utils.create_restricted_vocabulary(ILifeCycle['archival_value'],
                                                       ARCHIVAL_VALUE_OPTIONS,
                                                       message_factory=_),
                    provides = schema.interfaces.IVocabularyFactory,
                    name = u'lifecycle_archival_value_vocabulary')
form.default_value(field=ILifeCycle['archival_value'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['archival_value'],
        default = ARCHIVAL_VALUE_UNCHECKED
        )
    )


