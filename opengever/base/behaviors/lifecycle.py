from zope import schema
from zope.interface import alsoProvides, Interface
import zope.component
from z3c.form import validator

from five import grok

from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot

from opengever.base import _
from opengever.base.behaviors import utils



from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from opengever.base.interfaces import IBaseCustodyPeriods
from opengever.base.interfaces import IRetentionPeriodRegister


@grok.provider(IContextSourceBinder)
def custody_periods(context):
    voc = []
    terms = []
    registry = queryUtility(IRegistry)
    proxy = registry.forInterface(IBaseCustodyPeriods)
    voc = getattr(proxy, 'custody_periods')
    for term in voc:
        terms.append(SimpleVocabulary.createTerm(term))
    return SimpleVocabulary(terms)


class ILifeCycleMarker(Interface):
    pass



class ILifeCycle(form.Schema):

    form.fieldset(
        u'lifecycle',
        label = _(u'fieldset_lifecycle', default=u'Life Cycle'),
        fields = [
            u'retention_period',
            u'archival_value',
            u'custody_period',
            ],
        )

    retention_period = schema.Choice(
        title = _(u'label_retention_period', u'Retention period (years)'),
        description = _(u'help_retention_period', default=u''),
        source = u'lifecycle_retention_period_vocabulary',
        required = True,
        )

    archival_value = schema.Choice(
        title = _(u'label_archival_value', default=u'Archival value'),
        description = _(u'help_archival_value', default=u'Archival value code'),
        source = u'lifecycle_archival_value_vocabulary',
        required = True,
        )

    custody_period = schema.Choice(
        title = _(u'label_custody_period', default=u'Custody period (years)'),
        description = _(u'help_custody_period', default=u''),
        source = custody_periods,
        required = True,
        )


alsoProvides(ILifeCycle, IFormFieldProvider)

# RETENTION PERIOD: Vocabulary and default value
def _get_retention_period_options(vocabulary):
    registry = zope.component.getUtility(IRegistry)
    proxy = registry.forInterface(IRetentionPeriodRegister)
    options = []
    for num in getattr(proxy, 'retention_period'):
        num = int(num)
        options.append((num, num))
    return options
grok.global_utility(utils.create_restricted_vocabulary(
        ILifeCycle['retention_period'],
        _get_retention_period_options,
        message_factory=_),
                    provides=schema.interfaces.IVocabularyFactory,
                    name=u'lifecycle_retention_period_vocabulary')


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


# CUSTODY PERIOD / RETENTION PERIOD

class IntLowerEqualThanParentValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(IntLowerEqualThanParentValidator, self).validate(value)
        # should not be negative
        if int(value)<0:
            raise schema.interfaces.TooSmall()
        # get parent value
        if '++add++' in self.request.get('PATH_TRANSLATED', object()):
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


# custody_period
class CustodyPeriodValidator(IntLowerEqualThanParentValidator):
    pass
validator.WidgetValidatorDiscriminators(
    CustodyPeriodValidator,
    field=ILifeCycle['custody_period']
    )
form.default_value(field=ILifeCycle['custody_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['custody_period'],
        default = '10'
        )
    )
zope.component.provideAdapter(CustodyPeriodValidator)


# retention_period
class RetentionPeriodValidator(IntLowerEqualThanParentValidator):
    pass
validator.WidgetValidatorDiscriminators(
    RetentionPeriodValidator,
    field=ILifeCycle['retention_period']
    )

form.default_value(field=ILifeCycle['retention_period'])(
    utils.set_default_with_acquisition(
        field=ILifeCycle['retention_period'],
        default = 10
        )
    )
zope.component.provideAdapter(RetentionPeriodValidator)
