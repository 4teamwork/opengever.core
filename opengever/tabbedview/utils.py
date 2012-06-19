from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from zope.i18n import translate
from opengever.task.util import getTaskTypeVocabulary
from opengever.task.task import ITask
from Acquisition import aq_inner, aq_parent


@ram.cache(lambda m, c, r: 'translated_transitions_cache_key')
def get_translated_transitions(context, request):
    """Return all translated transitions from every workflows"""

    wft = getToolByName(context, 'portal_workflow')
    states = {}
    for wid in wft.getWorkflowIds():
        for state in wft.get(wid).states:
            states[state] = translate(state, domain='plone', context=request)
    return states


@ram.cache(lambda m, c, r: 'translated_types_cache_key')
def get_translated_types(context, request):
    values = {}
    for key, terms in getTaskTypeVocabulary(context).by_value.items():
        values[key] = terms.title.lower()

    return values


def get_containg_document_tab_url(context):
    """return the url to the `Documents` tab on containing object"""

    parent = aq_parent(aq_inner(context))

    if ITask.providedBy(parent):
        tab = 'relateddocuments'
    else:
        tab = 'documents'

    mtool = getToolByName(context, 'portal_membership')
    if mtool.checkPermission('View', parent):
        return '%s#%s' % (parent.absolute_url(), tab)
    else:
        return context.absolute_url()
