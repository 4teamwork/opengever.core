from opengever.base.utils import language_cache_key
from opengever.task.util import getTaskTypeVocabulary
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.i18n import translate


@ram.cache(language_cache_key)
def get_translated_transitions(context, request):
    """Return all translated transitions from every workflows"""

    wft = getToolByName(context, 'portal_workflow')
    states = {}
    for wid in wft.getWorkflowIds():
        for state in wft.get(wid).states:
            states[state] = translate(state, domain='plone', context=request)
    return states


@ram.cache(language_cache_key)
def get_translated_types(context, request):
    values = {}
    for key, terms in getTaskTypeVocabulary(context).by_value.items():
        values[key] = terms.title.lower()

    return values


def get_containing_document_tab_url(context):
    """return the url to the `Documents` tab on containing object"""

    finder = getAdapter(context, name='parent-dossier-finder')
    dossier = finder.find_dossier()

    tab = 'documents'

    mtool = getToolByName(context, 'portal_membership')
    if dossier and mtool.checkPermission('View', dossier):
        return '%s#%s' % (dossier.absolute_url(), tab)
    else:
        return context.absolute_url()
