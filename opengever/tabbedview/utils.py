from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from zope.i18n import translate


@ram.cache(lambda m, c, r: 'translated_transitions_cache_key')
def get_translated_transitions(context, request):
    """Return all translated transitions from every workflows"""

    wft = getToolByName(context, 'portal_workflow')
    states = {}
    for wid in wft.getWorkflowIds():
        for state in wft.get(wid).states:
            states[state] = translate(state, domain='plone', context=request)
    return states
