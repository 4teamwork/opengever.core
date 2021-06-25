from opengever.base.adapters import DefaultMovabilityChecker
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.templatefolder.utils import is_within_templates
from opengever.private.utils import is_within_private_root
from opengever.repository.utils import is_within_repository
from zExceptions import Forbidden
from zope.component import adapter


@adapter(IBaseDocument)
class DocumentMovabiliyChecker(DefaultMovabilityChecker):

    def validate_movement(self, target):
        if is_within_repository(self.context):
            if is_within_templates(target):
                raise Forbidden(
                    u'Documents within the repository cannot be moved to the templates.')
            if is_within_private_root(target):
                raise Forbidden(
                    u'Documents within the repository cannot be moved to the private repository.')
