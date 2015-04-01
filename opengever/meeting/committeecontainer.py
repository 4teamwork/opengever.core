from opengever.meeting import _
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice


sablon_template_source = ObjPathSourceBinder(
    portal_type=("opengever.meeting.sablontemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatedossier.interfaces.ITemplateDossier',
             'opengever.meeting.sablontemplate.ISablonTemplate',
             ],
        }
)


class ICommitteeContainer(form.Schema):
    """Base schema for a the committee container.
    """

    pre_protocol_template = RelationChoice(
        title=_('Pre-protocol template'),
        source=sablon_template_source,
        required=True,
    )

    protocol_template = RelationChoice(
        title=_('Protocol template'),
        source=sablon_template_source,
        required=True,
    )

    excerpt_template = RelationChoice(
        title=_('Excerpt template'),
        source=sablon_template_source,
        required=True,
    )


class CommitteeContainer(Container):
    """Committee Container class, a container for all committees."""
