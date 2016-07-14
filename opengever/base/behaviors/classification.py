from five import grok
from opengever.base import _
from opengever.base.behaviors import utils
from opengever.base.behaviors.utils import create_simple_vocabulary
from opengever.base.behaviors.utils import RestrictedVocabularyFactory
from opengever.base.utils import language_cache_key
from plone import api
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.memoize import ram
from zope import schema
from zope.i18n import translate
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


@ram.cache(language_cache_key)
def translated_public_trial_terms(context, request):
    values = {}
    for term in PUBLIC_TRIAL_OPTIONS:
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
        title=u'Public Trial default value',
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


classification_vf = RestrictedVocabularyFactory(
    IClassification['classification'],
    CLASSIFICATION_OPTIONS,
    message_factory=_,
    restricted=lambda: True)


# XXX: Eventually rewrite this as a context aware defaultFactory
form.default_value(field=IClassification['classification'])(
    utils.set_default_with_acquisition(
        field=IClassification['classification'],
        default=CLASSIFICATION_UNPROTECTED
    )
)

# TODO: This will be rewritten to eliminate one level of factories
public_trial_vf_factory = create_simple_vocabulary(
    PUBLIC_TRIAL_OPTIONS,
    message_factory=_)


# PRIVACY_LAYER: Vocabulary and default value
PRIVACY_LAYER_NO = u'privacy_layer_no'
PRIVACY_LAYER_YES = u'privacy_layer_yes'
PRIVACY_LAYER_OPTIONS = (
    (1, PRIVACY_LAYER_NO),
    (2, PRIVACY_LAYER_YES),
)


privacy_layer_vf = RestrictedVocabularyFactory(
    IClassification['privacy_layer'],
    PRIVACY_LAYER_OPTIONS,
    message_factory=_,
    restricted=lambda: True)


# XXX: Eventually rewrite this as a context aware defaultFactory
form.default_value(field=IClassification['privacy_layer'])(
    utils.set_default_with_acquisition(
        field=IClassification['privacy_layer'],
        default=PRIVACY_LAYER_NO
    )
)


class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification[
        'classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification[
        'privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification[
        'public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification[
        'public_trial_statement'])
