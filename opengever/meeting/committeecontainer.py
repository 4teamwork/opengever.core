from opengever.meeting import _
from opengever.meeting.sources import sablon_template_source
from plone.dexterity.content import Container
from plone.directives import form
from z3c.relationfield.schema import RelationChoice


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

    def get_pre_protocol_template(self):
        return self.pre_protocol_template.to_object

    def get_protocol_template(self):
        return self.protocol_template.to_object

    def get_excerpt_template(self):
        return self.excerpt_template.to_object
