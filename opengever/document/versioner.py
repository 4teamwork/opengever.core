from opengever.base.security import elevated_privileges
from opengever.document import _
from plone import api
from Products.CMFEditions.interfaces.IModifier import ModifierException
from Products.CMFEditions.Permissions import SaveNewVersion
from zope.annotation import IAnnotations
from zope.globalrequest import getRequest
from zope.i18n import translate
import time
import transaction


CUSTOM_INITIAL_VERSION_COMMENT = 'custom_initial_version_comment'


class Versioner(object):
    """Wrapper class for the CMF editions versioning, wich is used for the
    document versioning.
    """

    def __init__(self, document):
        self.document = document
        self.repository = api.portal.get_tool('portal_repository')

    def is_versionable(self):
        return self.repository.isVersionable(self.document)

    def get_history_metadata(self):
        return self.repository.getHistoryMetadata(self.document)

    def get_version_metadata(self, version_id):
        return self.get_history_metadata().retrieve(version_id)['metadata']

    def create_version(self, comment):
        """Creates a new version in CMFEditions.
        """
        self.repository.save(obj=self.document, comment=comment)

    def has_initial_version(self):
        return self.get_history_metadata() != []

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
        if self.has_initial_version():
            return

        if self.get_custom_initial_version_comment():
            comment = self.get_custom_initial_version_comment()
        else:
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

        creator = self.document.Creator()

        try:
            # Create the initial version using a temporary security manager
            # that claims a user ID of the user that was the creator of the
            # document.
            #
            # This will execute the version creation with Manager privileges,
            # but the given user_id.
            #
            # We need to do this this way because setting
            # sys_metadata['principal'] to the current user ID is hardcoded
            # in Products.CMFEditions.ArchivistTool.PreparedObject.__init__
            with elevated_privileges(user_id=creator):
                self.repository._recursiveSave(
                    self.document, metadata, sys_metadata,
                    autoapply=self.repository.autoapply)
        except ModifierException:
            # modifiers can abort save operations under certain conditions
            sp.rollback()
            raise

        self.remove_custom_initial_version_comment()

    def retrieve(self, version_id):
        """Returns the versioned object of the given version id.
        """
        return self.retrieve_version(version_id).object

    def retrieve_version(self, version_id):
        """Returns the VersionData of the given version id.
        """
        return self.repository.retrieve(self.document, version_id)

    def set_custom_initial_version_comment(self, comment):
        """It stores the given comment, which will be used when creating
        the initial version, temporarily in the annotations of the object.
        """
        annotations = IAnnotations(self.document)
        annotations[CUSTOM_INITIAL_VERSION_COMMENT] = comment

    def get_custom_initial_version_comment(self):
        return IAnnotations(self.document).get(CUSTOM_INITIAL_VERSION_COMMENT)

    def remove_custom_initial_version_comment(self):
        annotations = IAnnotations(self.document)

        if CUSTOM_INITIAL_VERSION_COMMENT in annotations:
            annotations.pop(CUSTOM_INITIAL_VERSION_COMMENT)
