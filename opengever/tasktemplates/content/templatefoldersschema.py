from opengever.tasktemplates import _
from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


sequence_types = SimpleVocabulary(
    [SimpleTerm(value=u'parallel', title=_(u'Parallel')),
     SimpleTerm(value=u'sequential', title=_(u'Sequential'))])


class ITaskTemplateFolderSchema(model.Schema):
    """Marker Schema for TaskTemplateFolder"""

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'sequence_type'])

    directives.order_after(sequence_type='IOpenGeverBase.description')
    sequence_type = schema.Choice(
        title=_(u'label_sequence_type', default='Type'),
        vocabulary=sequence_types,
        required=True,
    )
