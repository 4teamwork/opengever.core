from Products.CMFCore.utils import getToolByName
from opengever.base.behaviors.classification import PUBLIC_TRIAL_OPTIONS
from opengever.task.util import getTaskTypeVocabulary
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.i18n import translate


def translation_cache_key(mth, ctx, req):
    """
    Generates cache key used for functions with different output depending on
    the current language.
    """
    portal_state = getMultiAdapter((ctx, req), name=u'plone_portal_state')
    key = "%s.%s:%s" % (mth.__module__, mth.__name__, portal_state.language())
    return key


@ram.cache(translation_cache_key)
def get_translated_transitions(context, request):
    """Return all translated transitions from every workflows"""

    wft = getToolByName(context, 'portal_workflow')
    states = {}
    for wid in wft.getWorkflowIds():
        for state in wft.get(wid).states:
            states[state] = translate(state, domain='plone', context=request)
    return states


@ram.cache(translation_cache_key)
def get_translated_types(context, request):
    values = {}
    for key, terms in getTaskTypeVocabulary(context).by_value.items():
        values[key] = terms.title.lower()

    return values


@ram.cache(translation_cache_key)
def get_translated_public_trial_values(context, request):
    portal = getSite()

    values = {}
    for key, term in PUBLIC_TRIAL_OPTIONS:
        values[term] = portal.translate(term, context=request,
                                        domain="opengever.base")

    return values


def get_containg_document_tab_url(context):
    """return the url to the `Documents` tab on containing object"""

    finder = getAdapter(context, name='parent-dossier-finder')
    dossier = finder.find_dossier()

    tab = 'documents'

    mtool = getToolByName(context, 'portal_membership')
    if dossier and mtool.checkPermission('View', dossier):
        return '%s#%s' % (dossier.absolute_url(), tab)
    else:
        return context.absolute_url()
