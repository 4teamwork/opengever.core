
from zope import schema
from zope.interface import alsoProvides
from zope.schema import vocabulary

from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form

from opengever.repository import _

def make_vocabulary(opts):
    terms = [vocabulary.SimpleTerm(o, title=_(o)) for o in opts]
    return vocabulary.SimpleVocabulary(terms)


CLASSIFICATION_UNPROTECTED = u'unprotected'
CLASSIFICATION_CONFIDENTIAL = u'confidential'
CLASSIFICATION_CLASSIFIED = u'classified'
CLASSIFICATION_VOCABULARY = (
    CLASSIFICATION_UNPROTECTED,
    CLASSIFICATION_CONFIDENTIAL,
    CLASSIFICATION_CLASSIFIED,
)

PUBLIC_TRIAL_UNCHECKED = u'unchecked'
PUBLIC_TRIAL_PUBLIC = u'public'
PUBLIC_TRIAL_PRIVATE = u'private'
PUBLIC_TRIAL_VOCABULARY = (
    PUBLIC_TRIAL_UNCHECKED,
    PUBLIC_TRIAL_PUBLIC,
    PUBLIC_TRIAL_PRIVATE,
)


class IClassification(form.Schema):

    form.fieldset(
        u'classification',
        label = _(u'fieldset_classification', default=u'Classification'),
        fields = [
                u'classification',
                u'privacy_layer',
                u'public_trial',
                u'public_trial_statement',
                u'archival_value',
                u'custody_period',
                u'retention_period',
        ],
    )

    classification = schema.Choice(
            title = _(u'label_classification', default=u'Classification'),
            description = _(u'help_classification', default=u''),
            source = make_vocabulary(CLASSIFICATION_VOCABULARY),
            default = CLASSIFICATION_UNPROTECTED,
    )

    privacy_layer = schema.Bool(
            title = _(u'label_privacy_layer', default=u'Privacy layer'),
            description = _(u'help_privacy_layer', default=u''),
            default = False,
    )

    public_trial = schema.Choice(
            title = _(u'label_public_trial', default=u'Public Trial'),
            description = _(u'help_public_trial', default=u''),
            source = make_vocabulary(PUBLIC_TRIAL_VOCABULARY),
            default = PUBLIC_TRIAL_UNCHECKED,
    )

    public_trial_statement = schema.Text(
            title = _(u'label_public_trial_statement', default=u'Public trial statement'),
            description = _(u'help_public_trial_statement', default=u'Begrüundung Schutzgrad'),
            required = False,
            default = u'',
    )

    archival_value = schema.Int(
            title = _(u'label_archival_value', default=u'Archival value'),
            description = _(u'help_archival_value', default=u'Archival value code'),
            required = False,
    )

    custody_period = schema.Int(
            title = _(u'label_custody_period', default=u'Custody period (years)'),
            description = _(u'help_custody_period', default=u''),
            default = 10,
    )

    retention_period = schema.Int(
            title = _(u'label_retention_period', u'Retention period (years)'),
            description = _(u'help_retention_period', default=u''),
            default = 10,
    )


alsoProvides(IClassification, IFormFieldProvider)


class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification['classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification['privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification['public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification['public_trial_statement'])
    archival_value = metadata.DCFieldProperty(IClassification['archival_value'])
    custody_period = metadata.DCFieldProperty(IClassification['custody_period'])
    retention_period = metadata.DCFieldProperty(IClassification['retention_period'])


