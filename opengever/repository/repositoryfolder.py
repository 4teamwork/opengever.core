from Acquisition import aq_inner, aq_parent
from five import grok
from z3c.form import validator
from z3c.form import error
from zope import schema
from zope.interface import implements, invariant, Invalid
import zope.component

from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity.behaviors import metadata

from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder


class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'effective_title',
            u'reference_number',
            u'description',
            ],
        )

    #form.omitted('title')
    form.order_before(effective_title = '*')
    effective_title = schema.TextLine(
        title = _(u'Title'),
        required = True
        )

    reference_number = schema.Int(
        title = _(u'label_reference_number', default=u'Reference'),
        description = _(u'help_reference_number', default=u''),
        required = False,
        min = 1,
        )

    description = schema.Text(
        title = _(u'label_description', default=u'Description'),
        description =  _(u'help_description', default=u'A short summary of the content.'),
        required = False,
        )

    creators = schema.Tuple(
        title = _( u'label_creators', default=u'Creators' ),
        description = _( u'help_creators', default=u'' ),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.omitted('creators')


@form.default_value(field=IRepositoryFolderSchema['reference_number'])
def reference_number_default_value(data):
    highest_reference_number = 0
    for obj in data.context.listFolderContents():
        if IRepositoryFolder.providedBy(obj):
            if obj.reference_number > highest_reference_number:
                highest_reference_number = obj.reference_number
    highest_reference_number += 1
    return highest_reference_number


class ReferenceNumberValidator(validator.SimpleFieldValidator):
    """
    Reference number is uniqe per container (folder).
    """
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
    field=IRepositoryFolderSchema['reference_number']
    )
zope.component.provideAdapter(ReferenceNumberValidator)
zope.component.provideAdapter(error.ErrorViewMessage(
        _('error_sibling_reference_number_existing', default=u'A Sibling with the same reference number is existing'),
        error = schema.interfaces.ConstraintNotSatisfied,
        field = IRepositoryFolderSchema['reference_number'],
        ),
                              name = 'message'
                              )


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    creators = metadata.DCFieldProperty( IRepositoryFolderSchema['creators'],
                                         get_name = 'listCreators',
                                         set_name = 'setCreators')

    def __init__( self, *args, **kwargs ):
        content.Container.__init__( self, *args, **kwargs )
        #self.addCreator()

    def Title(self):
        title = u' %s' % self.effective_title
        obj = self
        while IRepositoryFolder.providedBy(obj):
            if hasattr(obj, 'reference_number'):
                title = unicode(obj.reference_number) + '.' + title
            obj = aq_parent(aq_inner(obj))
        return title

    def allowedContentTypes(self, *args, **kwargs):
        types = super(RepositoryFolder, self).allowedContentTypes(*args, **kwargs)
        # check if self contains any similar objects
        contains_similar_objects = False
        for id, obj in self.contentItems():
            if obj.portal_type==self.portal_type:
                contains_similar_objects = True
                break
        # get fti of myself
        fti = self.portal_types.get(self.portal_type)
        # filter content types, if required
        if contains_similar_objects:
            # only allow same types
            types = filter(lambda a:a==fti, types)
        return types



class NameFromTitle(grok.Adapter):
    """ An INameFromTitle adapter for namechooser
    gets the name from effective_title
    """
    grok.implements(INameFromTitle)
    grok.context(IRepositoryFolder)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.effective_title
