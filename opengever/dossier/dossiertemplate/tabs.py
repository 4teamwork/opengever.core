from five import grok
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.templatefolder.tabs import TemplateFolderDocuments
from opengever.dossier.templatefolder.tabs import TemplateFolderDossierTemplates
from opengever.tabbedview.browser.bumblebee_gallery import DocumentsGallery
from opengever.tabbedview.browser.tabs import DocumentsProxy


class DossierTemplateSubDossiers(TemplateFolderDossierTemplates):
    grok.context(IDossierTemplateMarker)
    grok.name('tabbedview_view-subdossiers')

    search_options = {'is_subdossier': True}


class DossierTemplateDocumentsProxy(DocumentsProxy):
    grok.context(IDossierTemplateMarker)
    grok.name('tabbedview_view-documents-proxy')


class DossierTemplateDocuments(TemplateFolderDocuments):
    grok.context(IDossierTemplateMarker)
    grok.name('tabbedview_view-documents')

    # Reset depth from super-class because we want do display
    # all sub-docouments in the dossiertemplate.
    depth = -1
    sort_on = 'sortable_title'


class DossierTemplateDocumentsGallery(DocumentsGallery):
    grok.context(IDossierTemplateMarker)
    grok.name('tabbedview_view-documents-gallery')

    sort_on = 'sortable_title'
