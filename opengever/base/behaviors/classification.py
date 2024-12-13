from opengever.base import _
from opengever.base.acquisition import acquired_default_factory
from opengever.base.utils import language_cache_key
from opengever.base.vocabulary import wrap_vocabulary
from plone import api
from plone.app.dexterity.behaviors import metadata
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.memoize import ram
from plone.supermodel import model
from zope import schema
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
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

# CLASSIFICATION: default value
CLASSIFICATION_UNPROTECTED = u'unprotected'


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


class IClassification(model.Schema):

    model.fieldset(
        u'classification',
        label=_(u'fieldset_classification', default=u'Classification'),
        fields=[
            u'classification',
            u'privacy_layer',
            u'public_trial',
            u'public_trial_statement',
        ],
    )

    form.write_permission(classification='opengever.base.EditLifecycleAndClassification')
    classification = schema.Choice(
        title=_(u'label_classification', default=u'Classification'),
        description=_(u'help_classification', default=u''),
        source=wrap_vocabulary(
            u'opengever.base.classifications',
            hidden_terms_from_registry='opengever.base.behaviors.IClassificationSettings.hidden_classifications'),
        required=True,
    )

    form.write_permission(privacy_layer='opengever.base.EditLifecycleAndClassification')
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
        title=u'Public Trial default value',
        source=u'classification_public_trial_vocabulary',
        required=True,
        default=PUBLIC_TRIAL_UNCHECKED
    )
    hidden_classifications = schema.List(
        title=u"Classification",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.base.classifications',
        ),
        default=list(),
        missing_value=list(),
        required=False
    )
    classification_default_value = schema.Choice(
        title=u'Classification default value',
        source=u'opengever.base.classifications',
        required=True,
        default=CLASSIFICATION_UNPROTECTED
    )


@provider(IContextAwareDefaultFactory)
def classification_default(context):
    default_factory = acquired_default_factory(
        field=IClassification['classification'],
        default=CLASSIFICATION_UNPROTECTED)
    return default_factory(context)


IClassification['classification'].defaultFactory = classification_default


# PRIVACY_LAYER: Vocabulary and default value
PRIVACY_LAYER_NO = u'privacy_layer_no'
PRIVACY_LAYER_YES = u'privacy_layer_yes'
PRIVACY_LAYER_CHOICES = (
    PRIVACY_LAYER_NO,
    PRIVACY_LAYER_YES,
)


def privacy_layer_vf(context):
    return SimpleVocabulary([
        SimpleTerm(choice, title=_(choice))
        for choice in PRIVACY_LAYER_CHOICES])


@provider(IContextAwareDefaultFactory)
def privacy_layer_default(context):
    default_factory = acquired_default_factory(
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
