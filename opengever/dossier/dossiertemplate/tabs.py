from opengever.dossier.templatefolder.tabs import TemplateFolderDocuments
from opengever.dossier.templatefolder.tabs import TemplateFolderDossierTemplates
from opengever.tabbedview.browser.bumblebee_gallery import DocumentsGallery
from opengever.tabbedview.browser.tabs import DocumentsProxy


class DossierTemplateSubDossiers(TemplateFolderDossierTemplates):

    search_options = {'is_subdossier': True}


class DossierTemplateDocumentsProxy(DocumentsProxy):
    """Document proxy view for the document tab of a dossier template.
    """


class DossierTemplateDocuments(TemplateFolderDocuments):

    # Reset depth from super-class because we want do display
    # all sub-docouments in the dossiertemplate.
    depth = -1
    sort_on = 'sortable_title'
    sort_order = 'ascending'


class DossierTemplateDocumentsGallery(DocumentsGallery):

    sort_on = 'sortable_title'
    sort_order = 'ascending'
