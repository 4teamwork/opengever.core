from opengever.base.source import RepositoryPathSourceBinder
from opengever.document import _
from plone.directives import form
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides


class IRelatedDocuments(form.Schema):
    """The 'Related documents' behvavior is an opengever.document
    specific 'Related items' behavior. Only allows references to
    opengever.documents.
    """

    relatedItems = RelationList(
        title=_(u'label_related_documents', default=u'Related Documents'),
        default=[],
        value_type=RelationChoice(
            title=u"Related",
            source=RepositoryPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.repository.repositoryroot.IRepositoryRoot',
                         'opengever.repository.repositoryfolder.' +
                            'IRepositoryFolderSchema',
                         'opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.document.document.IDocumentSchema',
                         'ftw.mail.mail.IMail', ]
                }),
            ),
        required=False,
        )

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'relatedItems',
            ],
        )


alsoProvides(IRelatedDocuments, form.IFormFieldProvider)
