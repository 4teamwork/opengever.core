from opengever.dossier import _
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.browser.bumblebee_gallery import BumblebeeGalleryMixin
from opengever.tabbedview.browser.tabs import BaseTabProxy
from opengever.tabbedview.browser.tabs import Documents, Trash
from opengever.tabbedview.helper import linked


REMOVED_COLUMNS = ['receipt_date', 'delivery_date', 'containing_subdossier']


def drop_columns(columns):

    cleaned_columns = []

    for col in columns:
        if isinstance(col, dict):
            if col.get('column') in REMOVED_COLUMNS:
                continue
        cleaned_columns.append(col)
    return cleaned_columns


class TemplateFolderDocuments(Documents):
    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateFolderDocuments, self).columns)

    @property
    def enabled_actions(self):
        return filter(
            lambda x: x not in self.disabled_actions,
            super(TemplateFolderDocuments, self).enabled_actions)

    disabled_actions = [
        'cancel',
        'checkin',
        'checkout',
        'create_task',
        'send_as_email',
        'submit_additional_documents',
    ]


class TemplateFolderSablonTemplates(Documents):

    types = ['opengever.meeting.sablontemplate']

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateFolderSablonTemplates, self).columns)

    @property
    def enabled_actions(self):
        return filter(
            lambda x: x not in self.disabled_actions,
            super(TemplateFolderSablonTemplates, self).enabled_actions)

    disabled_actions = [
        'cancel',
        'checkin',
        'checkout',
        'create_task',
        'move_items',
        'send_as_email',
        'submit_additional_documents',
    ]


class TemplateFolderProposalTemplatesProxy(BaseTabProxy):
    """This proxyview is looking for the last used documents
    view (list or gallery) and reopens this view.
    """


class TemplateFolderProposalTemplates(Documents):

    types = ['opengever.meeting.proposaltemplate']

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateFolderProposalTemplates, self).columns)

    @property
    def enabled_actions(self):
        return filter(
            lambda x: x not in self.disabled_actions,
            super(TemplateFolderProposalTemplates, self).enabled_actions)

    disabled_actions = [
        'cancel',
        'checkin',
        'checkout',
        'create_task',
        'move_items',
        'send_as_email',
        'submit_additional_documents',
    ]


class TemplateFolderProposalTemplatesGallery(BumblebeeGalleryMixin, TemplateFolderProposalTemplates):

    sort_on = 'sortable_title'

    @property
    def list_view_name(self):
        return 'proposaltemplates'


class TemplateFolderTrash(Trash):
    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateFolderTrash, self).columns)


class TemplateFolderDossierTemplates(BaseCatalogListingTab):

    filterlist_available = False
    sort_on = 'sortable_title'
    show_selects = False

    object_provides = IDossierTemplateSchema.__identifier__

    search_options = {'is_subdossier': False}

    columns = (

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},
        {'column': 'Description',
         'column_title': _(u'label_description', default=u'Description')},


        )

    enabled_actions = []
    major_actions = []
