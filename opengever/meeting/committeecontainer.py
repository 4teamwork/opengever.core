from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.meeting import _
from opengever.meeting import require_word_meeting_feature
from opengever.meeting.model import Member
from opengever.meeting.sources import proposal_template_source
from opengever.meeting.sources import sablon_template_source
from opengever.meeting.wrapper import MemberWrapper
from plone.dexterity.content import Container
from plone.directives import form
from z3c.relationfield.schema import RelationChoice


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

    agendaitem_list_template = RelationChoice(
        title=_('label_agendaitem_list_template',
                default=u'Agendaitem list template'),
        source=sablon_template_source,
        required=False,
    )

    toc_template = RelationChoice(
        title=_('label_toc_template',
                default=u'Table of contents template'),
        source=sablon_template_source,
        required=False,
    )

    ad_hoc_template = RelationChoice(
        title=_('label_ad_hoc_template',
                default=u'Ad hoc agenda item template'),
        source=proposal_template_source,
        required=False,
    )

    paragraph_template = RelationChoice(
        title=_('label_paragraph_template',
                default=u'Paragraph template'),
        source=sablon_template_source,
        required=False,
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

    def get_agendaitem_list_template(self):
        if self.agendaitem_list_template:
            return self.agendaitem_list_template.to_object

        return None

    def get_toc_template(self):
        if self.toc_template:
            return self.toc_template.to_object

        return None

    @require_word_meeting_feature
    def get_ad_hoc_template(self):
        if self.ad_hoc_template:
            return self.ad_hoc_template.to_object

        return None

    @require_word_meeting_feature
    def get_paragraph_template(self):
        if self.paragraph_template:
            return self.paragraph_template.to_object

        return None
