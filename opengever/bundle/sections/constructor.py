from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.interfaces import IDontIssueDossierReferenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from plone.dexterity.utils import createContentInContainer
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import classProvides
from zope.interface import implements
from zope.interface import noLongerProvides
import logging


logger = logging.getLogger('opengever.bundle.constructor')
logger.setLevel(logging.INFO)


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
        self.item_by_guid = self.transmogrifier.item_by_guid

        self.site = api.portal.get()
        self.ttool = api.portal.get_tool(u'portal_types')

    def has_translated_title(self, fti):
        return ITranslatedTitle.__identifier__ in fti.behaviors

    def __iter__(self):
        for item in self.previous:
            portal_type = item[u'_type']

            parent_guid = item.get(u'parent_guid')
            if parent_guid:
                context = self.item_by_guid[parent_guid][u'_object']
            else:
                context = self.site

            fti = self.ttool.getTypeInfo(portal_type)
            if fti is None:
                raise InvalidType(portal_type)

            try:
                # we need the title sometimes to auto-generate ids
                # XXX maybe be a bit more intelligent here and set all required
                # fields while constructing?
                if self.has_translated_title(fti):
                    title_keys = TRANSLATED_TITLE_NAMES
                else:
                    title_keys = (u'title',)

                title_args = dict((key, item.get(key)) for key in title_keys)

                with NoDossierReferenceNumbersIssued():
                    # Create the object without automatically issuing a
                    # reference number - we might want to set it explicitly
                    obj = createContentInContainer(
                        context, portal_type, **title_args)

                    if IDossierMarker.providedBy(obj):
                        prefix_adapter = IReferenceNumberPrefix(context)
                        if not prefix_adapter.get_number(obj):
                            # Set the local reference number part for the
                            # dossier if provided in item, otherwise have
                            # the adapter issue the next one
                            local_refnum = item.get('reference_number')
                            if local_refnum is not None:
                                prefix_adapter.set_number(obj, local_refnum)
                            else:
                                prefix_adapter.set_number(obj)

                parent_path = '/'.join(context.getPhysicalPath())
                logger.info("Constructed %r" % obj)
            except ValueError as e:
                logger.warning(
                    u'Could not create object at {} with guid {}. {}'.format(
                        parent_path, item['guid'], e.message))
                continue

            # build path relative to plone site
            item[u'_path'] = '/'.join(obj.getPhysicalPath()[2:])
            item[u'_object'] = obj

            yield item
