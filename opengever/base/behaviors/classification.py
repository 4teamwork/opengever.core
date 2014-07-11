from five import grok
from opengever.base import _
from opengever.base.behaviors import utils
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides, Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


# PUBLIC TRIAL: Vocabulary and default value
PUBLIC_TRIAL_UNCHECKED = u'unchecked'
PUBLIC_TRIAL_PUBLIC = u'public'
PUBLIC_TRIAL_PRIVATE = u'private'
PUBLIC_TRIAL_LIMITED_PUBLIC = u'limited-public'
PUBLIC_TRIAL_OPTIONS = (
    PUBLIC_TRIAL_UNCHECKED,
    PUBLIC_TRIAL_PUBLIC,
    PUBLIC_TRIAL_LIMITED_PUBLIC,
    PUBLIC_TRIAL_PRIVATE,
)


class IClassification(form.Schema):

    form.fieldset(
        u'classification',
        label=_(u'fieldset_classification', default=u'Classification'),
        fields=[
            u'classification',
            u'privacy_layer',
            u'public_trial',
            u'public_trial_statement',
        ],
    )

    classification = schema.Choice(
        title=_(u'label_classification', default=u'Classification'),
        description=_(u'help_classification', default=u''),
        source=u'classification_classification_vocabulary',
        required=True,
    )

    privacy_layer = schema.Choice(
        title=_(u'label_privacy_layer', default=u'Privacy layer'),
        description=_(u'help_privacy_layer', default=u''),
        source=u'classification_privacy_layer_vocabulary',
        required=True,
    )

    public_trial = schema.Choice(
        title=_(u'label_public_trial', default=u'Public Trial'),
        description=_(u'help_public_trial', default=u''),
        source=u'classification_public_trial_vocabulary',
        required=True,
    )

    public_trial_statement = schema.Text(
        title=_(u'label_public_trial_statement',
                default=u'Public trial statement'),
        description=_(u'help_public_trial_statement', default=u''),
        required=False,
        default=u'',
    )


alsoProvides(IClassification, IFormFieldProvider)


class IClassificationMarker(Interface):
    pass


class IClassificationSettings(Interface):
    """Registry settings interface for settings related to the IClassification
    behavior.
    """

    public_trial_default_value = schema.Choice(
        title=_(u'label_public_trial_default_value',
                default=u'Public Trial default value'),
        description=_(u'help_public_trial_default_value', default=u''),
        source=u'classification_public_trial_vocabulary',
        required=True,
        default=PUBLIC_TRIAL_UNCHECKED
    )


@grok.subscribe(IClassificationMarker, IObjectModifiedEvent)
def validate_children(folder, event):
    aq_fields = [
        IClassification['classification'],
        IClassification['privacy_layer']]

    utils.overrides_child(folder, event, aq_fields, IClassificationMarker)

# CLASSIFICATION: Vocabulary and default value
CLASSIFICATION_UNPROTECTED = u'unprotected'
CLASSIFICATION_CONFIDENTIAL = u'confidential'
CLASSIFICATION_CLASSIFIED = u'classified'
CLASSIFICATION_OPTIONS = (
    # Option-   # Option Name
    # level     #
    (1, CLASSIFICATION_UNPROTECTED),
    (2, CLASSIFICATION_CONFIDENTIAL),
    (3, CLASSIFICATION_CLASSIFIED),
)


grok.global_utility(
    utils.create_restricted_vocabulary(
        IClassification['classification'],
        CLASSIFICATION_OPTIONS,
        message_factory=_),
    provides=schema.interfaces.IVocabularyFactory,
    name=u'classification_classification_vocabulary')


form.default_value(field=IClassification['classification'])(
    utils.set_default_with_acquisition(
        field=IClassification['classification'],
        default=CLASSIFICATION_UNPROTECTED
    )
)


grok.global_utility(
    utils.create_simple_vocabulary(
        options=PUBLIC_TRIAL_OPTIONS,
        message_factory=_),
    provides=schema.interfaces.IVocabularyFactory,
    name=u'classification_public_trial_vocabulary')


# PRIVACY_LAYER: Vocabulary and default value
PRIVACY_LAYER_NO = u'privacy_layer_no'
PRIVACY_LAYER_YES = u'privacy_layer_yes'
PRIVACY_LAYER_OPTIONS = (
    (1, PRIVACY_LAYER_NO),
    (2, PRIVACY_LAYER_YES),
)


grok.global_utility(
    utils.create_restricted_vocabulary(
        IClassification['privacy_layer'],
        PRIVACY_LAYER_OPTIONS,
        message_factory=_),
    provides=schema.interfaces.IVocabularyFactory,
    name=u'classification_privacy_layer_vocabulary')


form.default_value(field=IClassification['privacy_layer'])(
    utils.set_default_with_acquisition(
        field=IClassification['privacy_layer'],
        default=PRIVACY_LAYER_NO
    )
)


# XXX: Setting the default value in the field directly, breaks the
# DCFieldProperty stuff. thus we implement the default value this way.
@form.default_value(field=IClassification['public_trial'])
def default_public_trial(data):
    """Set the actual date as default document_date"""
    return PUBLIC_TRIAL_UNCHECKED


class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification[
        'classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification[
        'privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification[
        'public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification[
        'public_trial_statement'])
