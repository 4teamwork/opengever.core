from five import grok
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.meeting.service import meeting_service
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone import api


class CommitteeVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.CommitteeVocabulary')

    def __call__(self, context):
        terms = []

        for committee in meeting_service().all_committees():
            terms.append(SimpleTerm(value=committee,
                                    token=committee.committee_id,
                                    title=committee.title))
        return SimpleVocabulary(terms)


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
            SimpleVocabulary.createTerm(member,
                                        str(member.member_id),
                                        member.fullname))

    return SimpleVocabulary(members)


class LanguagesVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.LanguagesVocabulary')

    def __call__(self, context):
        ltool = api.portal.get_tool('portal_languages')
        languages = [code.split('-')[0]
                     for code in ltool.getSupportedLanguages()]

        return SimpleVocabulary(
            [SimpleTerm(language) for language in languages])
