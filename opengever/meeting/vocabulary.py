from opengever.dossier.templatefolder import get_template_folder
from opengever.meeting.model import Committee
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.meeting.proposaltemplate import IProposalTemplate
from operator import attrgetter
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class CommitteeVocabulary(object):
    """Vocabulary with all committees.

    Contains committees as term values.  Is currently used to set a meeting's
    committee.
    """
    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value=committee,
                       token=str(committee.committee_id),
                       title=committee.title)
            for committee in self.get_committees()
        ])

    def get_committees(self):
        return Committee.query.order_by('title').all()


@implementer(IVocabularyFactory)
class ActiveCommitteeVocabulary(object):
    """Vocabulary with all active committees.

    Contains committee OGUID as term values. Is currently used to set a
    proposal's committee.
    """
    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value=unicode(committee.oguid),
                       token=str(committee.oguid),
                       title=committee.title)
            for committee in self.get_committees()
        ])

    def get_committees(self):
        return Committee.query.active().order_by('title').all()


@implementer(IVocabularyFactory)
class MeetingTemplateVocabulary(object):

    def __call__(self, context):
        terms = []

        meeting_templates = api.content.find(
            portal_type='opengever.meeting.meetingtemplate')

        for brain in meeting_templates:
            template = brain.getObject()
            terms.append(SimpleTerm(
                value=template,
                token=template.id,
                title=safe_unicode(template.title)))

        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class MemberVocabulary(object):

    def __call__(self, context):
        terms = []

        for member in Member.query.order_by(Member.fullname):
            terms.append(SimpleTerm(value=member,
                                    token=member.member_id,
                                    title=member.fullname))
        return SimpleVocabulary(terms)


@provider(IContextSourceBinder)
def get_committee_member_vocabulary(meetingwrapper):
    meeting = meetingwrapper.model
    members = []
    for membership in Membership.query.for_meeting(meeting):
        member = membership.member
        members.append(
            SimpleVocabulary.createTerm(
                member,
                str(member.member_id),
                member.get_title(show_email_as_link=False)))

    return SimpleVocabulary(members)


@implementer(IVocabularyFactory)
class AdHocAgendaItemTemplatesForCommitteeVocabulary(object):
    """The AdHocAgendaItemTemplatesForCommitteeVocabulary is used in the
    proposal add form for selecting an ad-hoc agenda item template.

    The ad-hoc agenda item template field is configured so that the list of
    templates is re-rendered whenever the user changes the committee.
    This allows this vocubulary to ask the selected committee whether the
    list of templates is limited. If so, the templates are reduced to the
    allowed templates.
    """

    def __call__(self, context):
        template_folder = get_template_folder()
        if template_folder is None:
            # this may happen when the user does not have permissions to
            # view templates and/or during ++widget++ traversal
            return SimpleVocabulary([])

        allowed_uids = self.get_allowed_ad_hoc_agenda_item_templates_UIDS(context)
        objects = self.get_ad_hoc_agenda_item_templates(template_folder, allowed_uids)
        return self.make_vocabulary_from_objects(objects)

    def get_ad_hoc_agenda_item_templates(self, template_folder, allowed_uids):
        """Return a list of regular ad-hoc agenda item templates.
        This list includes all visible ad-hoc agenda item templates.
        When a list of "allowed_uids" is passed in, it is used as filter
        so that documents without a listed UID are removed.
        """
        query = {'context': template_folder,
                 'depth': -1,
                 'portal_type': "opengever.meeting.proposaltemplate",
                 'sort_on': 'sortable_title',
                 'sort_order': 'ascending'}

        if allowed_uids:
            query['UID'] = allowed_uids

        return [brain.getObject() for brain in api.content.find(**query)]

    def get_allowed_ad_hoc_agenda_item_templates_UIDS(self, context):
        committee = self.get_committee(context)
        if not committee:
            return None

        return committee.resolve_committee().allowed_ad_hoc_agenda_item_templates

    def get_committee(self, context):
        committees = context.REQUEST.form.get('form.widgets.committee', None)
        if committees:
            return Committee.query.filter_by(committee_id=int(committees[0])).one()

        return None

    def make_vocabulary_from_objects(self, objects):
        terms = []
        for template in objects:
            terms.append(SimpleVocabulary.createTerm(
                template,
                IUUID(template),
                safe_unicode(template.Title())))
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class ProposalTemplatesForCommitteeVocabulary(object):
    """The ProposalTemplatesForCommitteeVocabulary is used in the
    proposal add form for selecting a proposal template.

    The proposal template field is configured so that the list of templates
    is re-rendered whenever the user changes the committee.
    This allows this vocubulary to ask the selected committee whether the
    list of templates is limited. If so, the templates are reduced to the
    allowed templates.

    Additional, when a successor proposal is created, the vocabulary allows
    the user to select the proposal document of the predecess as template
    for the new proposal.
    """

    def __call__(self, context):
        template_folder = get_template_folder()
        if template_folder is None:
            # this may happen when the user does not have permissions to
            # view templates and/or during ++widget++ traversal
            return SimpleVocabulary([])

        allowed_uids = self.get_allowed_proposal_templates_UIDS(context)
        objects = self.get_predecessor_proposal_documents(context.REQUEST)
        objects.extend(self.get_proposal_templates(template_folder, allowed_uids))
        return self.make_vocabulary_from_objects(objects)

    def get_predecessor_proposal_documents(self, request):
        """Return a list of documents from the predecessor proposal.
        The returned documents can additionally be selected as proposal template.
        """
        predecessor_path = request.form.get('form.widgets.predecessor_proposal', None)
        if predecessor_path and predecessor_path != u'--NOVALUE--':
            # The ++add++opengever.meeting.proposal was opened with a predecessor.
            # We should also offer to use the predecessor proposal document as
            # "template".
            predecessor_path = safe_unicode(predecessor_path).encode('utf-8')
            predecessor = api.content.get(path=predecessor_path)
            return [predecessor.get_proposal_document()]
        return []

    def get_proposal_templates(self, template_folder, allowed_uids):
        """Return a list of regular proposal templates.
        This list includes all visible proposal templates.
        When a list of "allowed_uids" is passed in, it is used as filter
        so that documents without a listed UID are removed.
        """
        query = {'context': template_folder,
                 'depth': -1,
                 'portal_type': "opengever.meeting.proposaltemplate",
                 'sort_on': 'sortable_title',
                 'sort_order': 'ascending'}

        if allowed_uids:
            query['UID'] = allowed_uids

        return [brain.getObject() for brain in api.content.find(**query)]

    def get_allowed_proposal_templates_UIDS(self, context):
        committee = self.get_committee(context)
        if not committee:
            return None

        return committee.resolve_committee().allowed_proposal_templates

    def get_committee(self, context):
        committees = context.REQUEST.form.get('form.widgets.committee', None)
        if committees:
            return Committee.query.filter_by(committee_id=int(committees[0])).one()

        return None

    def make_vocabulary_from_objects(self, objects):
        terms = []
        for template in objects:
            terms.append(SimpleVocabulary.createTerm(
                template,
                IUUID(template),
                safe_unicode(template.Title())))
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class LanguagesVocabulary(object):

    def __call__(self, context):
        ltool = api.portal.get_tool('portal_languages')
        supported_language_codes = [language[0].split('-')[0] for language in ltool.listSupportedLanguages()]
        return SimpleVocabulary([
            SimpleVocabulary.createTerm(*LanguagesVocabulary.parse_language_to_term(language))
            for language in ltool.listAvailableLanguageInformation()
            if language.get('code') in supported_language_codes
            ])

    @staticmethod
    def parse_language_to_term(language):
        code = language.get('code')
        name = language.get('native')
        return code, code, name


@implementer(IVocabularyFactory)
class ProposalTemplatesVocabulary(object):

    def __call__(self, context):
        terms = []
        for brain in api.content.find(object_provides=IProposalTemplate):
            terms.append(SimpleTerm(value=brain.UID,
                                    token=brain.UID,
                                    title=safe_unicode(brain.Title)))

        terms.sort(key=attrgetter('title'))
        return SimpleVocabulary(terms)
