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

    def _construct_object(self, container, portal_type, item):
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

    def __iter__(self):
        for item in self.previous:
            portal_type = item[u'_type']

            parent_guid = item.get(u'parent_guid')
            if parent_guid:
                path = self.bundle.item_by_guid[parent_guid][u'_path']
                context = traverse(self.site, path, None)
            elif item.get(u'parent_ref_number'):
                path = self.bundle.path_by_reference_number.get(
                    item[u'parent_ref_number'])
                if not path:
                    logger.warning(
                        u'Could not create object with guid `{}`, parent with '
                        'reference number `{}` not found.'.format(
                            item['guid'], item[u'parent_ref_number']))
                    continue

                context = traverse(self.site, path, None)
            else:
                context = self.site

            parent_path = '/'.join(context.getPhysicalPath())

            try:
                obj = self._construct_object(context, portal_type, item)
                logger.info("Constructed %r" % obj)
            except ValueError as e:
                logger.warning(
                    u'Could not create object at {} with guid {}. {}'.format(
                        parent_path, item['guid'], e.message))
                continue

            # build path relative to plone site
            item[u'_path'] = '/'.join(obj.getPhysicalPath()[2:])

            yield item
