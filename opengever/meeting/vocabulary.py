from five import grok
from opengever.dossier.templatefolder import get_template_folder
from opengever.meeting.model import Committee
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class CommitteeVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.CommitteeVocabulary')

    def __call__(self, context):
        terms = []

        for committee in self.get_committees():
            terms.append(SimpleTerm(value=committee,
                                    token=committee.committee_id,
                                    title=committee.title))
        return SimpleVocabulary(terms)

    def get_committees(self):
        return Committee.query.all()


class ActiveCommitteeVocabulary(CommitteeVocabulary):
    grok.name('opengever.meeting.ActiveCommitteeVocabulary')

    def get_committees(self):
        return Committee.query.active().all()


class MemberVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.MemberVocabulary')

    def __call__(self, context):
        terms = []

        for member in Member.query.order_by(Member.fullname):
            terms.append(SimpleTerm(value=member,
                                    token=member.member_id,
                                    title=member.fullname))
        return SimpleVocabulary(terms)


@grok.provider(IContextSourceBinder)
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


@provider(IContextSourceBinder)
def get_proposal_template_vocabulary(context):
    template_folder = get_template_folder()
    if template_folder is None:
        # this may happen when the user does not have permissions to
        # view templates and/or during ++widget++ traversal
        return SimpleVocabulary([])

    templates = api.content.find(
        context=template_folder,
        depth=-1,
        portal_type="opengever.meeting.proposaltemplate",
        sort_on='sortable_title', sort_order='ascending')

    terms = []
    for brain in templates:
        template = brain.getObject()
        terms.append(SimpleVocabulary.createTerm(
            template,
            IUUID(template),
            safe_unicode(brain.Title)))
    return SimpleVocabulary(terms)


class LanguagesVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.LanguagesVocabulary')

    def __call__(self, context):
        ltool = api.portal.get_tool('portal_languages')
        languages = [code.split('-')[0]
                     for code in ltool.getSupportedLanguages()]

        return SimpleVocabulary(
            [SimpleTerm(language) for language in languages])
