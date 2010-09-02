from zope.interface import alsoProvides
from plone.app.dexterity.behaviors.related import IRelatedItems
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form
from opengever.document import _

class IRelatedDocuments(form.Schema):
    """The relatedDocument behvavior is a opengever.document 
    specific relateditems behavior. Only allows opengever.documents
    """

    relatedItems = RelationList(
        title=_(u'label_related_documents', default=u'Related Documents'),
        default=[],
        value_type=RelationChoice(title=u"Related",
            source=ObjPathSourceBinder(
                portal_type="opengever.document.document", ),
        ),
        required=False,
        )

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'relatedItems',
            ],
        )


alsoProvides(IRelatedDocuments, form.IFormFieldProvider)