import re
from zope.interface import Interface, alsoProvides, implements
from zope import schema
from zope.component import adapts, provideAdapter
from five import grok

from plone.app.dexterity.behaviors import metadata
from plone.directives import form
from plone.indexer import indexer

from z3c.form import validator, error

from opengever.base import _
from opengever.base.interfaces import IReferenceNumber as IReferenceNumberAdapter

class IReferenceNumber(form.Schema):

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'reference_number',
            ],
        )

    reference_number = schema.TextLine(
        title = _(u'label_reference_number', default=u'Reference'),
        description = _(u'help_reference_number', default=u''),
        required = False,
        )

alsoProvides(IReferenceNumber, form.IFormFieldProvider)

@form.default_value(field=IReferenceNumber['reference_number'])
def reference_number_default_value(data):
    val = 0
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
                if num > val:
                    val = num
    # then increase by one, if possible:
    # if its a number, we increase the whole number
    try:
        val = str(int(val) + 1)
    except (ValueError, TypeError):
        pass
    else:
        return val
    # .. otherwise try to increment the last numeric part
    xpr = re.compile('\d+')
    matches = tuple(xpr.finditer(val))
    if len(matches)>0:
        span = matches[-1].span()
        subvalue = val[span[0]:span[1]]
        try:
            subvalue = int(subvalue)
        except (ValueError, TypeError):
            pass
        else:
            subvalue += 1
            subvalue = str(subvalue)
            val = val[:span[0]] + subvalue + val[span[1]:]
            return val
    # ... if we have no number, we can't do anything..
    return ''

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

@indexer(IReferenceNumberMarker)
def reference_number(obj):
    return IReferenceNumberAdapter(obj).get_number()
grok.global_adapter(reference_number, name='reference_number')
