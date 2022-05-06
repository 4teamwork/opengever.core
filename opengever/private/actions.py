from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.docugate import is_docugate_feature_enabled
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.private.dossier import IPrivateDossier
from plone import api
from zope.component import adapter


@adapter(IPrivateDossier, IOpengeverBaseLayer)
class PrivateDossierContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)

    def is_document_from_docugate_available(self):
        return api.user.has_permission('Add portal content', obj=self.context) \
            and is_docugate_feature_enabled()

    def is_document_with_oneoffixx_template_available(self):
        return api.user.has_permission('Add portal content', obj=self.context) \
            and is_oneoffixx_feature_enabled()

    def is_document_with_template_available(self):
        return api.user.has_permission('Add portal content', obj=self.context)

    def is_zipexport_available(self):
        return True
