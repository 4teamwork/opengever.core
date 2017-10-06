from opengever.document import _
from plone import api
from Products.CMFEditions.interfaces.IModifier import ModifierException
from Products.CMFEditions.Permissions import SaveNewVersion
from zope.globalrequest import getRequest
from zope.i18n import translate
import time
import transaction


class Versioner(object):
    """Wrapper class for the CMF editions versioning, wich is used for the
    document versioning.
    """

    def __init__(self, document):
        self.document = document
        self.repository = api.portal.get_tool('portal_repository')

    def _get_history(self):
        return self.repository.getHistoryMetadata(self.document)

    def create_version(self, comment):
        """Creates a new version in CMFEditions.
        """
        self.repository.save(obj=self.document, comment=comment)

    def has_initial_version(self):
        return self._get_history() != []

    def get_current_version_id(self, missing_as_zero=False):
        repository = api.portal.get_tool("portal_repository")

        if not self.has_initial_version():
            # initial version has not been created yet, but will be created
            # before the file is changed
            if missing_as_zero:
                return 0
            else:
                return None

        history = repository.getHistoryMetadata(self.document)
        current_version = history.getLength(countPurged=False) - 1

        return current_version

    def create_initial_version(self):
        """Creates an initial version for the document.

        Copied from `Products.CMFEditions.CopyModifyMergeRepositoryTool.save`
        only the timestamp is changed to the creation timestamp.
        """
        comment = _(u'initial_document_version_change_note',
                    default=u'Initial version')
        comment = translate(comment, context=getRequest())

        self.repository._assertAuthorized(self.document, SaveNewVersion, 'save')
        sp = transaction.savepoint(optimistic=True)
        sys_metadata = self.repository._prepareSysMetadata(comment)

        # Set creation datetime as initial version timestamp,
        # cmfeditions stores unix timestamps without any timezone information
        # therefore we have to do the same.
        created = self.document.created().asdatetime().replace(tzinfo=None)
        sys_metadata['timestamp'] = time.mktime(created.timetuple())
        metadata = {}

        try:
            self.repository._recursiveSave(
                self.document, metadata, sys_metadata,
                autoapply=self.repository.autoapply)
        except ModifierException:
            # modifiers can abort save operations under certain conditions
            sp.rollback()
            raise
