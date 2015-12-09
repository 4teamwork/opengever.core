from opengever.base import _
from z3c.form.validator import SimpleFieldValidator
from zope.interface import Invalid


class BaseRepositoryfolderValidator(SimpleFieldValidator):
    """This validator allows only repository folders that can contain a
    dossier.

    """
    def validate(self, value):
        super(BaseRepositoryfolderValidator, self).validate(value)

        if not self._is_dossier_addable(value):
            msg = _(u'You cannot add dossiers in the selected repository '
                    u'folder. Either you do not have the privileges or the '
                    u'repository folder contains another repository folder.')
            raise Invalid(msg)

    def _is_dossier_addable(self, repo_folder):
        # The user should be able to create a dossier (of any type) in the
        # selected repository folder.
        dossier_behavior = 'opengever.dossier.behaviors.dossier.IDossier'

        for fti in repo_folder.allowedContentTypes():
            if dossier_behavior in getattr(fti, 'behaviors', ()):
                return True

        return False
