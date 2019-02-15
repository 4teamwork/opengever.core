from zope.container.interfaces import IContainerModifiedEvent
from Acquisition import aq_parent, aq_inner
from opengever.base.interfaces import IReferenceNumberPrefix as PrefixAdapter
from opengever.repository import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form import validator, error
from z3c.form.interfaces import IAddForm
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def reference_number_prefix_default(context):
    """Determine the default for the reference number prefix.

    context: Usually the container where a new object is created (i.e.
    default factory is called during content creation), unless the factory
    is called from an edit or display action (which shouldn't happen).
    """
    if not context:
        # We don't have any context if using the /@types endpoint from the
        # plone rest-api.
        # See https://github.com/4teamwork/opengever.core/issues/5283
        return u''
    return PrefixAdapter(context).get_next_number()


class IReferenceNumberPrefix(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'reference_number_prefix',
            ],
        )

    reference_number_prefix = schema.TextLine(
        title=_(
            u'label_reference_number_prefix',
            default=u'Reference Prefix'),
        required=False,
        defaultFactory=reference_number_prefix_default,
        )


alsoProvides(IReferenceNumberPrefix, IFormFieldProvider)


class ReferenceNumberPrefixValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        # setting parent, for that we check if there are a Add- or a Editform
        super(ReferenceNumberPrefixValidator, self).validate(value)
        if IAddForm.providedBy(self.view.parentForm):
            if not PrefixAdapter(self.context).is_valid_number(value):
                raise schema.interfaces.ConstraintNotSatisfied()
        else:
            parent = aq_parent(aq_inner(self.context))
            if not PrefixAdapter(parent).is_valid_number(value, self.context):
                raise schema.interfaces.ConstraintNotSatisfied()


validator.WidgetValidatorDiscriminators(
    ReferenceNumberPrefixValidator,
    field=IReferenceNumberPrefix['reference_number_prefix'],
    )

ReferenceNumberPrefixErrorMessage = error.ErrorViewMessage(
    _('error_sibling_reference_number_existing',
      default=u'A Sibling with the same reference number is existing.'),
    error=schema.interfaces.ConstraintNotSatisfied,
    field=IReferenceNumberPrefix['reference_number_prefix'],
)


class IReferenceNumberPrefixMarker(Interface):
    """
    Marker Interface for the ReferenceNumber-Prefix Behavior
    """


def saveReferenceNumberPrefix(obj, event):
    """When an object providing IReferenceNumberPrefixMarker (repository
    folders) gets added or has been modified, make sure it has
    a unique reference number prefix.

    If necessary, set_number() creates a collision free prefix.
    """
    if IContainerModifiedEvent.providedBy(event):
        return

    parent = aq_parent(aq_inner(obj))

    # Mark the reference number as issued in the parent's annotations
    number = PrefixAdapter(parent).set_number(
        obj, IReferenceNumberPrefix(obj).reference_number_prefix)

    # Store the number on the actual object
    IReferenceNumberPrefix(obj).reference_number_prefix = number
