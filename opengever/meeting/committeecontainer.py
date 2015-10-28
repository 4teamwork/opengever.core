from opengever.meeting import _
from opengever.meeting.model import Member
from opengever.meeting.sources import sablon_template_source
from opengever.meeting.wrapper import MemberWrapper
from plone.dexterity.content import Container
from plone.directives import form
from z3c.relationfield.schema import RelationChoice
from opengever.base.behaviors.translated_title import TranslatedTitleMixin


class ICommitteeContainer(form.Schema):
    """Base schema for a the committee container.
    """

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


_marker = object()


class CommitteeContainer(Container, TranslatedTitleMixin):
    """Committee Container class, a container for all committees."""

    Title = TranslatedTitleMixin.Title

    def _getOb(self, id_, default=_marker):
        """We extend `_getOb` in order to change the context for member
        objects to `MemeberWrapper`. That allows us to register the
        members view as regular Browser view without any traversal hacks."""

        obj = super(CommitteeContainer, self)._getOb(id_, default)
        if obj is not default:
            return obj

        if id_.startswith('member'):
            member_id = int(id_.split('-')[-1])
            member = Member.query.get(member_id)
            if member:
                return MemberWrapper.wrap(self, member)

        if default is _marker:
            raise KeyError(id_)
        return default

    def get_protocol_template(self):
        return self.protocol_template.to_object

    def get_excerpt_template(self):
        return self.excerpt_template.to_object
