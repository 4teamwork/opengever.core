from five import grok
from opengever.dossier.templatedossier.interfaces import ITemplateDossier
from opengever.tabbedview.browser.tabs import Documents, Trash


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
        'send_as_email',
        'checkout',
        'checkin',
        'cancel',
        'move_items',
        'create_task',
    ]


class TemplateDossierTrash(Trash):
    grok.context(ITemplateDossier)

    depth = 1

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierTrash, self).columns)
