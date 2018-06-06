from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.meeting import _
from opengever.meeting.model import Member
from opengever.meeting.sources import proposal_template_source
from opengever.meeting.sources import sablon_template_source
from opengever.meeting.wrapper import MemberWrapper
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice


class ICommitteeContainer(model.Schema):
    """Base schema for a the committee container.
    """

    protocol_header_template = RelationChoice(
        title=_('label_protocol_header_template',
                default='Protocol header template'),
        source=sablon_template_source,
        required=True,
    )

    protocol_suffix_template = RelationChoice(
        title=_('label_protocol_suffix_template',
                default='Protocol suffix template'),
        source=sablon_template_source,
        required=False,
    )

    agenda_item_header_template = RelationChoice(
        title=_('label_agenda_item_header_template',
                default='Agenda item header template for the protocol'),
        source=sablon_template_source,
        required=False,
    )

    agenda_item_suffix_template = RelationChoice(
        title=_('label_agenda_item_suffix_template',
                default='Agenda item suffix template for the protocol'),
        source=sablon_template_source,
        required=False,
    )

    excerpt_header_template = RelationChoice(
        title=_('label_excerpt_header_template',
                default='Excerpt header template'),
        source=sablon_template_source,
        required=False,
    )

    excerpt_suffix_template = RelationChoice(
        title=_('label_excerpt_suffix_template',
                default='Excerpt suffix template'),
        source=sablon_template_source,
        required=False,
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

    def get_protocol_header_template(self):
        if self.protocol_header_template:
            return self.protocol_header_template.to_object
        return None

    def get_protocol_suffix_template(self):
        return getattr(self.protocol_suffix_template, 'to_object', None)

    def get_agenda_item_header_template(self):
        return getattr(self.agenda_item_header_template, 'to_object', None)

    def get_agenda_item_suffix_template(self):
        return getattr(self.agenda_item_suffix_template, 'to_object', None)

    def get_excerpt_header_template(self):
        if self.excerpt_header_template:
            return self.excerpt_header_template.to_object
        return None

    def get_excerpt_suffix_template(self):
        if self.excerpt_suffix_template:
            return self.excerpt_suffix_template.to_object
        return None

    def get_agendaitem_list_template(self):
        if self.agendaitem_list_template:
            return self.agendaitem_list_template.to_object

        return None

    def get_toc_template(self):
        if self.toc_template:
            return self.toc_template.to_object

        return None

    def get_ad_hoc_template(self):
        if self.ad_hoc_template:
            return self.ad_hoc_template.to_object

        return None

    def get_paragraph_template(self):
        if self.paragraph_template:
            return self.paragraph_template.to_object

        return None
