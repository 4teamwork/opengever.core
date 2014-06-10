from zope import schema
from zope.interface import alsoProvides, Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from five import grok

from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form


from opengever.base import _
from opengever.base.behaviors import utils


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

    #form.widget(privacy_layer=checkbox.SingleCheckBoxFieldWidget)
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


@grok.subscribe(IClassificationMarker, IObjectModifiedEvent)
def validate_children(folder, event):
    aq_fields = [
        IClassification['classification'],
        IClassification['public_trial'],
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


# PUBLIC: Vocabulary and default value
PUBLIC_TRIAL_UNCHECKED = u'unchecked'
PUBLIC_TRIAL_PUBLIC = u'public'
PUBLIC_TRIAL_PRIVATE = u'private'
PUBLIC_TRIAL_LIMITED_PUBLIC = u'limited-public'
PUBLIC_TRIAL_OPTIONS = (
    (1, PUBLIC_TRIAL_UNCHECKED),
    (2, PUBLIC_TRIAL_PUBLIC),
    (3, PUBLIC_TRIAL_LIMITED_PUBLIC),
    (4, PUBLIC_TRIAL_PRIVATE),
    )


grok.global_utility(
    utils.create_restricted_vocabulary(
        IClassification['public_trial'],
        PUBLIC_TRIAL_OPTIONS,
        message_factory=_),
    provides=schema.interfaces.IVocabularyFactory,
    name=u'classification_public_trial_vocabulary')


form.default_value(field=IClassification['public_trial'])(
    utils.set_default_with_acquisition(
        field=IClassification['public_trial'],
        default=PUBLIC_TRIAL_UNCHECKED
        )
    )


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


class Classification(metadata.MetadataBase):

    classification = metadata.DCFieldProperty(IClassification[
            'classification'])
    privacy_layer = metadata.DCFieldProperty(IClassification[
            'privacy_layer'])
    public_trial = metadata.DCFieldProperty(IClassification[
            'public_trial'])
    public_trial_statement = metadata.DCFieldProperty(IClassification[
            'public_trial_statement'])
