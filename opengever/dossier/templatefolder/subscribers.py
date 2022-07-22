from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_path_filter
from opengever.base.portlets import add_navigation_portlet_assignment
from opengever.base.portlets import block_context_portlet_inheritance
from opengever.base.security import elevated_privileges
from opengever.base.solr import batched_solr_results
from opengever.document.interfaces import ITemplateDocumentMarker
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from zope.component import queryUtility
from zope.container.interfaces import IContainerModifiedEvent


def configure_templatefolder_portlets(templatefolder, event):
    """Added Eventhandler which configure portlets:

     - Do not acquire portlets, when templatefolder is not a subtemplatefolder
     - Add navigation portlet assignments as context portlet
    """

    if templatefolder.is_subtemplatefolder():
        return

    block_context_portlet_inheritance(templatefolder)

    url_tool = api.portal.get_tool('portal_url')
    add_navigation_portlet_assignment(
        templatefolder,
        root=u'/'.join(url_tool.getRelativeContentPath(templatefolder)),
        topLevel=0)


def reindex_contained_documents(templatefolder, event):
    """When a templatefolder is modified, if the title has changed we reindex
    the containing_dossier index in all contained documents
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    attrs = tuple(
        attr
        for descr in event.descriptions
        for attr in descr.attributes
    )
    title_attrs = ['ITranslatedTitle.title_de', 'ITranslatedTitle.title_fr',
                   'ITranslatedTitle.title_en']
    for attr in title_attrs:
        if attr in attrs:
            languages = api.portal.get_tool('portal_languages').getSupportedLanguages()
            titles = [templatefolder.Title(language.split('-')[0]) for language in languages]
            containing_dossier_title = ' / '.join(titles)
            solr = queryUtility(ISolrSearch)
            filters = make_path_filter('/'.join(templatefolder.getPhysicalPath()), depth=-1)
            filters.append('object_provides:{}'.format(ITemplateDocumentMarker.__identifier__))

            with elevated_privileges():
                for batch in batched_solr_results(filters=filters, fl='UID'):
                    for doc in batch:
                        solr.manager.connection.add({
                            "UID": doc['UID'],
                            "containing_dossier": {"set": containing_dossier_title},
                        })
            return
