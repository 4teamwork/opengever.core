from zope.interface import Interface, alsoProvides, implements
from zope import schema
from zope.component import adapts, provideAdapter

from plone.app.dexterity.behaviors import metadata
from plone.directives import form

from z3c.form import validator, error

from opengever.base import _

class IReferenceNumber(form.Schema):

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'reference_number',
            ],
        )

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
    parent = None
    #XXX CHANGED FROM PATH_TRANSLATED TO PATH_INFO because the test don't work
    if '++add++' in data.context.REQUEST.get('PATH_INFO', object()):
        parent = data.context
        context = None
    else:
        parent = data.context.aq_inner.aq_parent
        context = data.context
    for obj in parent.listFolderContents():
        if IReferenceNumberMarker.providedBy(obj):
            if obj!=context:
                num = IReferenceNumber(obj).reference_number
                if num > highest_reference_number:
                    highest_reference_number = num
    highest_reference_number += 1
    return highest_reference_number

class ReferenceNumberValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        super(ReferenceNumberValidator, self).validate(value)
        #XXX CHANGED FROM PATH_TRANSLATED TO PATH_INFO because the test don't work
        if '++add++' in self.request.get('PATH_INFO', object()):
            # context is container
            siblings = self.context.getFolderContents(full_objects=1)
        else:
            parent = self.context.aq_inner.aq_parent
            siblings = filter(lambda a:a!=self.context,
                              parent.getFolderContents(full_objects=1))
        sibling_ref_nums = []
        for sibling in siblings:
            if IReferenceNumberMarker.providedBy(sibling):
                try:
                    proxy = IReferenceNumber(sibling)
                    sibling_ref_nums.append(self.field.get(proxy))
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
        _('error_sibling_reference_number_existing',
          default=u'A Sibling with the same reference number is existing'),
        error = schema.interfaces.ConstraintNotSatisfied,
        field = IReferenceNumber['reference_number'],
        ),
               name = 'message'
               )

class IReferenceNumberMarker(Interface):
    """
    Marker Interface for the ReferenceNumber Behavior
    """
