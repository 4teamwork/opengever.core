from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.interfaces import IDontIssueDossierReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from plone.dexterity.utils import createContentInContainer
from zope.annotation import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import classProvides
from zope.interface import implements
from zope.interface import noLongerProvides
import logging


logger = logging.getLogger('opengever.bundle.constructor')
logger.setLevel(logging.INFO)


BUNDLE_GUID_KEY = 'bundle_guid'

TYPES_WITHOUT_REFERENCE_NUMBER = (
    'opengever.task.task',
    'opengever.meeting.proposal',
    'opengever.meeting.submittedproposal',
    'opengever.disposition.disposition',
)


class InvalidType(Exception):
    pass


class NoDossierReferenceNumbersIssued(object):
    """Contextmanager that temporarily disables issuing of reference numbers
    for newly created dossiers.
    """

    def __enter__(self):
        alsoProvides(getRequest(), IDontIssueDossierReferenceNumber)

    def __exit__(self, exc_type, exc_val, exc_tb):
        noLongerProvides(getRequest(), IDontIssueDossierReferenceNumber)


class ConstructorSection(object):
    """OGGBundle specific constructor section.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

        self.site = api.portal.get()
        self.ttool = api.portal.get_tool(u'portal_types')
        self.catalog = api.portal.get_tool('portal_catalog')

        self.bundle.path_by_guid_cache = {}
        self.bundle.path_by_refnum_cache = {}
        self.bundle.constructed_guids = set()

    def _has_translated_title(self, fti):
        return ITranslatedTitle.__identifier__ in fti.behaviors

    def _get_fti(self, portal_type):
        fti = self.ttool.getTypeInfo(portal_type)
        if fti is None:
            raise InvalidType(portal_type)
        return fti

    def _get_title_args(self, fti, item):
        # we need the title sometimes to auto-generate ids
        # XXX maybe be a bit more intelligent here and set all required
        # fields while constructing?
        if self._has_translated_title(fti):
            title_keys = TRANSLATED_TITLE_NAMES
        else:
            title_keys = (u'title',)

        title_args = {}
        for key in title_keys:
            value = item.get(key)
            if value and not isinstance(value, unicode):
                value = value.decode('utf-8')

            title_args[key] = value

        return title_args

    def _set_guid(self, obj, item):
        """Store the GUID from the bundle in item's annotations in order to
        later be able to match up Plone objects with bundle items.
        """
        IAnnotations(obj)[BUNDLE_GUID_KEY] = item['guid']

    def _construct_object(self, container, item):
        portal_type = item['_type']
        fti = self._get_fti(portal_type)
        title_args = self._get_title_args(fti, item)

        with NoDossierReferenceNumbersIssued():
            # Create the object without automatically issuing a
            # reference number - we might want to set it explicitly
            obj = createContentInContainer(
                container, portal_type, **title_args)

            if IDossierMarker.providedBy(obj):
                prefix_adapter = IReferenceNumberPrefix(container)
                if not prefix_adapter.get_number(obj):
                    # Set the local reference number part for the
                    # dossier if provided in item, otherwise have
                    # the adapter issue the next one
                    local_refnum = item.get('reference_number')
                    if local_refnum is not None:
                        prefix_adapter.set_number(obj, local_refnum)
                    else:
                        prefix_adapter.set_number(obj)

        self._set_guid(obj, item)
        return obj

    def path_from_existing_guid(self, guid):
        if guid not in self.bundle.path_by_guid_cache:

            results = self.catalog.unrestrictedSearchResults(bundle_guid=guid)
            if len(results) == 0:
                # This should never happen, since we pre-validated GUIDs
                # in the ResolveGUIDSection
                logger.warning(
                    u"Couldn't find object with GUID %s in "
                    u"catalog" % guid)
                return

            if len(results) > 1:
                # Ambiguous GUID - this should never happen
                logger.warning(
                    u"Ambiguous GUID! Found more than one result in catalog "
                    u"for GUID %s " % guid)
                return

            brain = results[0]
            path = self.get_relative_path(brain)
            self.bundle.path_by_guid_cache[guid] = path

        return self.bundle.path_by_guid_cache[guid]

    def path_from_guid(self, guid):
        if guid in self.bundle.existing_guids:
            # Object with referenced GUID already exists in Plone
            return self.path_from_existing_guid(guid)

        # Othwerise determine parent path from pipeline item
        return self.bundle.item_by_guid[guid]['_path']

    def path_from_refnum(self, formatted_refnum):
        if formatted_refnum not in self.bundle.path_by_refnum_cache:

            results = self.catalog.unrestrictedSearchResults(
                reference=formatted_refnum,
                portal_type={'not': TYPES_WITHOUT_REFERENCE_NUMBER})

            if len(results) == 0:
                # This should never happen, since we pre-validated refnums
                # in the ResolveGUIDSection
                logger.warning(
                    u"Couldn't find reference number %s in "
                    u"catalog" % formatted_refnum)
                return

            if len(results) > 1:
                # With the 'not' constraint above, reference numbers should
                # unambiguously point to a single object - except for the
                # case where we're dealing with multiple repository roots.
                #
                # For that case, we would need to either specify the root
                # that should be considered, or fix reference numbers to be
                # unique across repository roots (which currently don't
                # contribute their own component to the reference number).
                logger.warning(
                    u"Found more than one matches in catalog for reference "
                    u"number %s" % formatted_refnum)
                return

            brain = results[0]
            path = self.get_relative_path(brain)
            self.bundle.path_by_refnum_cache[formatted_refnum] = path

        return self.bundle.path_by_refnum_cache[formatted_refnum]

    def get_relative_path(self, brain):
        """Returns the path relative to the plone site for the given brain.
        """
        return '/'.join(brain.getPath().split('/')[2:])

    def resolve_parent_pointer(self, item):
        """Resolves an item's parent pointer to a container obj and its path.
        """
        parent_guid = item.get('parent_guid')
        formatted_parent_refnum = item.get('_formatted_parent_refnum')

        if parent_guid is not None:
            parent_path = self.path_from_guid(parent_guid)

        elif formatted_parent_refnum is not None:
            parent_path = self.path_from_refnum(formatted_parent_refnum)

        elif item['_type'] == 'opengever.repository.repositoryroot':
            # Repo roots are the only type that don't require a parent
            # pointer, and get constructed directly in the Plone site
            container = self.site
            parent_path = '/'

        else:
            # Should never happen - schema requires a parent pointer
            logger.warning(
                u'Item with GUID %s is missing a parent pointer, '
                u'skipping.' % item['guid'])
            return

        if not parent_path:
            logger.warning(
                u'Could not determine parent container for item with '
                u'GUID %s, skipping.' % item['guid'])
            return

        container = traverse(self.site, parent_path, None)
        return container, parent_path

    def __iter__(self):
        for item in self.previous:
            parent = self.resolve_parent_pointer(item)
            if parent is None:
                # Failed to resolve parent, warnings have been logged
                continue

            container, parent_path = parent
            try:
                obj = self._construct_object(container, item)
                self.bundle.constructed_guids.add(item['guid'])
                logger.info(u'Constructed %r' % obj)
            except ValueError as e:
                logger.warning(
                    u'Could not create object at {} with guid {}. {}'.format(
                        parent_path, item['guid'], e.message))
                continue

            # build path relative to plone site
            item['_path'] = '/'.join(obj.getPhysicalPath()[2:])

            yield item
