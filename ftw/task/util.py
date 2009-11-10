from five import grok

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from ftw.task import _

@grok.provider(IContextSourceBinder)
def getManagersVocab(context):
    acl_users = getToolByName(context, 'acl_users')
    group = acl_users.getGroupById('Administrators')
    terms = []
    if group is not None:
        for member_id in group.getMemberIds():
            user = acl_users.getUserById(member_id)
            if user is not None:
                member_name = user.getProperty('fullname') or member_id
                terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

    return SimpleVocabulary(terms)

@grok.provider(IContextSourceBinder)
def getTransitionVocab(context):
    wftool = getToolByName(context, 'portal_workflow')
    transitions = []
    
    transitions.append(dict(value='', label=PMF(u'No change'),
                            checked="checked"))
    for tdef in wftool.getTransitionsFor(context):
        transitions.append(dict(value=tdef['id'],
                                label=tdef['title_or_id'], checked=''))
    return transitions
    