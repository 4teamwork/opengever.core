from five import grok
from opengever.base import _
from opengever.base.acquisition import set_default_with_acquisition
from opengever.base.restricted_vocab import propagate_vocab_restrictions
from opengever.base.restricted_vocab import RestrictedVocabularyFactory
from opengever.base.utils import language_cache_key
from plone import api
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.memoize import ram
from zope import schema
from zope.i18n import translate
from zope.interface import alsoProvides, Interface
from zope.interface import provider
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


# PUBLIC TRIAL: Vocabulary and default value
PUBLIC_TRIAL_UNCHECKED = u'unchecked'
PUBLIC_TRIAL_PUBLIC = u'public'
PUBLIC_TRIAL_PRIVATE = u'private'
PUBLIC_TRIAL_LIMITED_PUBLIC = u'limited-public'
PUBLIC_TRIAL_CHOICES = (
    PUBLIC_TRIAL_UNCHECKED,
    PUBLIC_TRIAL_PUBLIC,
    PUBLIC_TRIAL_LIMITED_PUBLIC,
    PUBLIC_TRIAL_PRIVATE,
)


def public_trial_vocabulary_factory(context):
    return SimpleVocabulary([
        SimpleTerm(msgid, title=_(msgid))
        for msgid in PUBLIC_TRIAL_CHOICES])


@ram.cache(language_cache_key)
def translated_public_trial_terms(context, request):
    values = {}
    for term in PUBLIC_TRIAL_CHOICES:
        values[term] = translate(term, context=request,
                                 domain="opengever.base")
    return values


def public_trial_default():
    """Default value for `public_trial` field for new documents.
    """
    return api.portal.get_registry_record(
        'public_trial_default_value', interface=IClassificationSettings)


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
        defaultFactory=public_trial_default,
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
        source=u'classification_public_trial_vocabulary',
        required=True,
        default=PUBLIC_TRIAL_UNCHECKED
    )


@grok.subscribe(IClassificationMarker, IObjectModifiedEvent)
def propagate_vocab_restrictions_to_children(container, event):
    restricted_fields = [
        IClassification['classification'],
        IClassification['privacy_layer']]

    propagate_vocab_restrictions(
        container, event, restricted_fields, IClassificationMarker)

# CLASSIFICATION: Vocabulary and default value
CLASSIFICATION_UNPROTECTED = u'unprotected'
CLASSIFICATION_CONFIDENTIAL = u'confidential'
CLASSIFICATION_CLASSIFIED = u'classified'
CLASSIFICATION_CHOICES = (
    # Choice-   # Choice Name
    # level     #
    (1, CLASSIFICATION_UNPROTECTED),
    (2, CLASSIFICATION_CONFIDENTIAL),
    (3, CLASSIFICATION_CLASSIFIED),
)


classification_vf = RestrictedVocabularyFactory(
    IClassification['classification'],
    CLASSIFICATION_CHOICES,
    message_factory=_,
    restricted=True)


@provider(IContextAwareDefaultFactory)
def classification_default(context):
    default_factory = set_default_with_acquisition(
        field=IClassification['classification'],
        default=CLASSIFICATION_UNPROTECTED)
    return default_factory(context)

IClassification['classification'].defaultFactory = classification_default


# PRIVACY_LAYER: Vocabulary and default value
PRIVACY_LAYER_NO = u'privacy_layer_no'
PRIVACY_LAYER_YES = u'privacy_layer_yes'
PRIVACY_LAYER_CHOICES = (
    (1, PRIVACY_LAYER_NO),
    (2, PRIVACY_LAYER_YES),
)


privacy_layer_vf = RestrictedVocabularyFactory(
    IClassification['privacy_layer'],
    PRIVACY_LAYER_CHOICES,
    message_factory=_,
    restricted=True)


@provider(IContextAwareDefaultFactory)
def privacy_layer_default(context):
    default_factory = set_default_with_acquisition(
        field=IClassification['privacy_layer'],
        default=PRIVACY_LAYER_NO)
    return default_factory(context)

IClassification['privacy_layer'].defaultFactory = privacy_layer_default


class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification[
        'classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification[
        'privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification[
        'public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification[
        'public_trial_statement'])
