
from zope import schema
from zope.interface import alsoProvides
import zope.component
from z3c.form.browser import checkbox
from z3c.form import validator

from five import grok

from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot

from opengever.repository import _
from opengever.repository import utils

class IClassification(form.Schema):

    form.fieldset(
        u'classification',
        label = _(u'fieldset_classification', default=u'Classification'),
        fields = [
                u'classification',
                u'privacy_layer',
                u'public_trial',
                u'public_trial_statement',
        ],
    )

    classification = schema.Choice(
            title = _(u'label_classification', default=u'Classification'),
            description = _(u'help_classification', default=u''),
            source = u'classification_classification_vocabulary',
            required = False,
    )

    #form.widget(privacy_layer=checkbox.SingleCheckBoxFieldWidget)
    privacy_layer = schema.Choice(
            title = _(u'label_privacy_layer', default=u'Privacy layer'),
            description = _(u'help_privacy_layer', default=u''),
            source = u'classification_privacy_layer_vocabulary',
            required = False,
    )

    public_trial = schema.Choice(
            title = _(u'label_public_trial', default=u'Public Trial'),
            description = _(u'help_public_trial', default=u''),
            source = u'classification_public_trial_vocabulary',
            required = False,
    )

    public_trial_statement = schema.Text(
            title = _(u'label_public_trial_statement', default=u'Public trial statement'),
            description = _(u'help_public_trial_statement', default=u'Begrüundung Schutzgrad'),
            required = False,
            default = u'',
    )

    form.fieldset(
        u'lifecycle',
        label = _(u'fieldset_lifecycle', default=u'Life Cycle'),
        fields = [
                u'retention_period',
                u'archival_value',
                u'custody_period',
        ],
    )

    retention_period = schema.Int(
            title = _(u'label_retention_period', u'Retention period (years)'),
            description = _(u'help_retention_period', default=u''),
            default = 10,
            required = False,
    )

    archival_value = schema.Choice(
            title = _(u'label_archival_value', default=u'Archival value'),
            description = _(u'help_archival_value', default=u'Archival value code'),
            source = u'classification_archival_value_vocabulary',
            required = False,
    )

    custody_period = schema.Int(
            title = _(u'label_custody_period', default=u'Custody period (years)'),
            description = _(u'help_custody_period', default=u''),
            default = 10,
            required = False,
    )

alsoProvides(IClassification, IFormFieldProvider)

# CLASSIFICATION: Vocabulary and default value
CLASSIFICATION_UNPROTECTED = u'unprotected'
CLASSIFICATION_CONFIDENTIAL = u'confidential'
CLASSIFICATION_CLASSIFIED = u'classified'
CLASSIFICATION_OPTIONS = (
    # Option-   # Option Name
    # level     #
    (1,         CLASSIFICATION_UNPROTECTED),
    (2,         CLASSIFICATION_CONFIDENTIAL),
    (3,         CLASSIFICATION_CLASSIFIED),
)
grok.global_utility(utils.create_restricted_vocabulary(IClassification['classification'],
                                                 CLASSIFICATION_OPTIONS,
                                                 message_factory=_),
                    provides = schema.interfaces.IVocabularyFactory,
                    name = u'classification_classification_vocabulary')
form.default_value(field=IClassification['classification'])(
        utils.set_default_with_acquisition(
                field=IClassification['classification'],
                default = CLASSIFICATION_CONFIDENTIAL
        )
)

# PUBLIC: Vocabulary and default value
PUBLIC_TRIAL_UNCHECKED = u'unchecked'
PUBLIC_TRIAL_PUBLIC = u'public'
PUBLIC_TRIAL_PRIVATE = u'private'
PUBLIC_TRIAL_OPTIONS = (
    (1,         PUBLIC_TRIAL_UNCHECKED),
    (2,         PUBLIC_TRIAL_PUBLIC),
    (3,         PUBLIC_TRIAL_PRIVATE),
)
grok.global_utility(utils.create_restricted_vocabulary(IClassification['public_trial'],
                                                 PUBLIC_TRIAL_OPTIONS,
                                                 message_factory=_),
                    provides = schema.interfaces.IVocabularyFactory,
                    name = u'classification_public_trial_vocabulary')
form.default_value(field=IClassification['public_trial'])(
        utils.set_default_with_acquisition(
                field=IClassification['public_trial'],
                default = PUBLIC_TRIAL_UNCHECKED
        )
)


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
grok.global_utility(utils.create_restricted_vocabulary(IClassification['archival_value'],
                                                 ARCHIVAL_VALUE_OPTIONS,
                                                 message_factory=_),
                    provides = schema.interfaces.IVocabularyFactory,
                    name = u'classification_archival_value_vocabulary')
form.default_value(field=IClassification['archival_value'])(
        utils.set_default_with_acquisition(
                field=IClassification['archival_value'],
                default = ARCHIVAL_VALUE_UNCHECKED
        )
)


# PRIVACY_LAYER: Vocabulary and default value
PRIVACY_LAYER_NO = u'privacy layer : no'
PRIVACY_LAYER_YES = u'privacy layer : yes'
PRIVACY_LAYER_OPTIONS = (
    (1,         PRIVACY_LAYER_NO),
    (2,         PRIVACY_LAYER_YES),
)
grok.global_utility(utils.create_restricted_vocabulary(IClassification['privacy_layer'],
                                                       PRIVACY_LAYER_OPTIONS,
                                                       message_factory=_),
                    provides = schema.interfaces.IVocabularyFactory,
                    name = u'classification_privacy_layer_vocabulary')
form.default_value(field=IClassification['privacy_layer'])(
        utils.set_default_with_acquisition(
                field=IClassification['privacy_layer'],
                default = PRIVACY_LAYER_NO
        )
)

# CUSTODY PERIOD / RETENTION PERIOD

class IntLowerEqualThanParentValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(IntLowerEqualThanParentValidator, self).validate(value)
        # should not be negative
        if int(value)<0:
            raise schema.interfaces.TooSmall()
        # get parent value
        if '++add++' in self.request.get('PATH_TRANSLATED', object()):
            obj = self.context
        else:
            obj = self.context.aq_inner.aq_parent
        parent_value = -1
        while parent_value<0 and not ISiteRoot.providedBy(obj):
            cf_obj = zope.component.queryAdapter(obj, IClassification)
            if cf_obj:
                try:
                    parent_value = int(self.field.get(cf_obj))
                except AttributeError:
                    pass
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
        field=IClassification['custody_period']
)
form.default_value(field=IClassification['custody_period'])(
        utils.set_default_with_acquisition(
                field=IClassification['custody_period'],
                default = 10
        )
)
zope.component.provideAdapter(CustodyPeriodValidator)


# retention_period
class RetentionPeriodValidator(IntLowerEqualThanParentValidator):
    pass
validator.WidgetValidatorDiscriminators(
        RetentionPeriodValidator,
        field=IClassification['retention_period']
)
form.default_value(field=IClassification['retention_period'])(
        utils.set_default_with_acquisition(
                field=IClassification['retention_period'],
                default = 10
        )
)
zope.component.provideAdapter(RetentionPeriodValidator)





class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification['classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification['privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification['public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification['public_trial_statement'])
    archival_value = metadata.DCFieldProperty(IClassification['archival_value'])
    custody_period = metadata.DCFieldProperty(IClassification['custody_period'])
    retention_period = metadata.DCFieldProperty(IClassification['retention_period'])


