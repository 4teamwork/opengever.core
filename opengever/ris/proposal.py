from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.interfaces import IReferenceNumber
from opengever.base.response import IResponseSupported
from opengever.base.source import DossierPathSourceBinder
from opengever.base.utils import to_html_xweb_intelligent
from opengever.dossier.utils import get_containing_dossier
from opengever.meeting import _
from opengever.ogds.base.sources import AssignedUsersSourceBinder
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implements


class IProposal(model.Schema):

    dexteritytextindexer.searchable("title")
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u"label_description", default=u'Description'),
        required=False,
        missing_value=u'',
        default=u'',
    )

    committee_title = schema.TextLine(
        title=_(u"label_committee_title", default=u"Committee title"),
        required=True,
    )
    committee_url = schema.TextLine(
        title=_(u"label_committee_url", default="Committee URL"),
        required=True,
    )

    meeting_title = schema.TextLine(
        title=_(u"label_meeting_title", default=u"Meeting title"),
        required=False,
    )
    meeting_url = schema.TextLine(
        title=_(u"label_meeting_url", default=u"Meeting URL"),
        required=False,
    )

    business_title = schema.TextLine(
        title=_(u"label_business_title", default=u"Business title"),
        required=False,
    )
    business_url = schema.TextLine(
        title=_(u"label_business_url", default=u"Business URL"),
        required=False,
    )

    # this corresponds to the sequence_number of an agenda item (per period)
    # the name follows the already user-visible name chosen for sablon
    decision_number = schema.TextLine(
        title=_(u"label_decision_number", default=u"Decision number"),
        required=False,
    )
    decision_number_formatted = schema.TextLine(
        title=_(u"label_decision_number_formatted", default=u"Formatted decision number"),
        required=False,
    )

    business_type = schema.TextLine(
        title=_(u"label_business_type", default=u"Business type"),
        required=False,
    )

    widget("issuer", KeywordFieldWidget, async=True)
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        source=AssignedUsersSourceBinder(),
        required=True,
    )

    widget("assignee", KeywordFieldWidget, async=True)
    assignee = schema.Choice(
        title=_(u"label_assignee", default=u"Assignee"),
        source=AssignedUsersSourceBinder(),
        required=False,
    )

    responsible = schema.TextLine(
        title=_(u"label_responsible", default=u"Responsible"),
        required=False,
        max_length=256,
    )

    topic = schema.TextLine(
        title=_(u"label_topic", default=u"Topic"),
        required=False,
        max_length=256,
    )

    document = RelationChoice(
        title=_(u"label_proposal_document", default=u"Proposal document"),
        default=None,
        missing_value=None,
        source=DossierPathSourceBinder(
            portal_type=("opengever.document.document",),
            navigation_tree_query={
                "review_state": {"not": "document-state-shadow"},
                "file_extension": ".docx",
                "object_provides": [
                    "opengever.document.document.IDocumentSchema",
                    "opengever.dossier.behaviors.dossier.IDossierMarker",
                    "opengever.task.task.ITask",
                ],
            },
        ),
        required=True,
    )

    attachments = RelationList(
        title=_(u"label_attachments", default=u"Attachments"),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Attachment",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    "review_state": {"not": "document-state-shadow"},
                    "object_provides": [
                        "ftw.mail.mail.IMail",
                        "opengever.document.document.IDocumentSchema",
                        "opengever.dossier.behaviors.dossier.IDossierMarker",
                        "opengever.task.task.ITask",
                    ],
                },
            ),
        ),
        required=False,
    )

    excerpts = RelationList(
        title=_(u"label_excerpts", default=u"Excerpts"),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Excerpt",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document",),
                navigation_tree_query={
                    "review_state": {"not": "document-state-shadow"},
                    "object_provides": [
                        "opengever.document.document.IDocumentSchema",
                        "opengever.dossier.behaviors.dossier.IDossierMarker",
                        "opengever.task.task.ITask",
                    ],
                },
            ),
        ),
        required=False,
    )


class Proposal(Container):

    implements(IProposal, IResponseSupported)

    def Title(self):
        return self.title.encode("utf-8")

    def get_description(self):
        return to_html_xweb_intelligent(self.description)

    def Description(self):
        return self.description.encode("utf-8")

    def get_containing_dossier(self):
        return get_containing_dossier(self)

    def get_repository_folder_title(self):
        main_dossier = self.get_containing_dossier().get_main_dossier()
        repository_folder = aq_parent(aq_inner(main_dossier))
        return repository_folder.Title(
            language=self.language, prefix_with_reference_number=False
        )

    def get_main_dossier_reference_number(self):
        return IReferenceNumber(self.get_main_dossier()).get_number()
