from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from plone import api


class DossierListingActions(BaseListingActions):

    def is_copy_items_available(self):
        return True

    def is_create_disposition_available(self):
        return api.user.has_permission('opengever.disposition: Add disposition')

    def is_edit_items_available(self):
        return True

    def is_export_dossiers_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_pdf_dossierlisting_available(self):
        return True


class PrivateDossierListingActions(BaseListingActions):

    def is_edit_items_available(self):
        return True

    def is_export_dossiers_available(self):
        return True

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)

    def is_pdf_dossierlisting_available(self):
        return True
