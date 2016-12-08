from five import grok
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.templatedossier.interfaces import ITemplateDossier
from opengever.tabbedview import _
from opengever.tabbedview import BaseCatalogListingTab
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


class TemplateDossierDocuments(Documents):
    grok.context(ITemplateDossier)

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierDocuments, self).columns)

    @property
    def enabled_actions(self):
        return filter(
            lambda x: x not in self.disabled_actions,
            super(TemplateDossierDocuments, self).enabled_actions)

    disabled_actions = [
        'cancel',
        'checkin',
        'checkout',
        'create_task',
        'move_items',
        'send_as_email',
        'submit_additional_documents',
    ]


class TemplateDossierSablonTemplates(Documents):
    grok.context(ITemplateDossier)
    grok.name('tabbedview_view-sablontemplates')

    types = ['opengever.meeting.sablontemplate']

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierSablonTemplates, self).columns)

    @property
    def enabled_actions(self):
        return filter(
            lambda x: x not in self.disabled_actions,
            super(TemplateDossierSablonTemplates, self).enabled_actions)

    disabled_actions = [
        'cancel',
        'checkin',
        'checkout',
        'create_task',
        'move_items',
        'send_as_email',
        'submit_additional_documents',
    ]


class TemplateDossierTrash(Trash):
    grok.context(ITemplateDossier)

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierTrash, self).columns)


class TemplateDossierDossierTemplates(BaseCatalogListingTab):
    grok.name('tabbedview_view-dossiertemplates')

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
