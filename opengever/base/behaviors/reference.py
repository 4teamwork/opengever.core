from zope.interface import Interface, alsoProvides, implements
from zope import schema
from zope.component import adapts, provideAdapter

from plone.app.dexterity.behaviors import metadata
from plone.directives import form

from z3c.form import validator, error

from opengever.base import _

class IReferenceNumber(form.Schema):
    
    reference_number = schema.Int(
            title = _(u'label_reference_number', default=u'Reference'),
            description = _(u'help_reference_number', default=u''),
            required = False,
            min = 1,
    )
    
alsoProvides(IReferenceNumber, form.IFormFieldProvider)
    
@form.default_value(field=IReferenceNumber['reference_number'])
def reference_number_default_value(data):
    highest_reference_number = 0
    for obj in data.context.listFolderContents():
        if IReferenceNumberMarker.providedBy(obj):
            if obj.reference_number > highest_reference_number:
                highest_reference_number = obj.reference_number
    highest_reference_number += 1
    return highest_reference_number
"""
class ReferenceNumberValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(ReferenceNumberValidator, self).validate(value)
        if '++add++' in self.request.get('PATH_TRANSLATED', object()):
            # context is container
            siblings = self.context.getFolderContents(full_objects=1)
        else:
            parent = self.context.aq_inner.aq_parent
            siblings = filter(lambda a:a!=self.context, parent.getFolderContents(full_objects=1))
        sibling_ref_nums = []
        for sibling in siblings:
            try:
                sibling_ref_nums.append(self.field.get(sibling))
            except AttributeError:
                pass
        if value in sibling_ref_nums:
            raise schema.interfaces.ConstraintNotSatisfied()

validator.WidgetValidatorDiscriminators(
        ReferenceNumberValidator,
        field=IReferenceNumber['reference_number']
)
provideAdapter(ReferenceNumberValidator)
provideAdapter(error.ErrorViewMessage(
                _('error_sibling_reference_number_existing', default=u'A Sibling with the same reference number is existing'),
                error = schema.interfaces.ConstraintNotSatisfied,
                field = IReferenceNumber['reference_number'],
        ),
        name = 'message'
)
"""

class IReferenceNumberMarker(Interface):
    """
    Marker Interface for the ReferenceNumber Behavior
    """