from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.setup.sections.bundlesource import BUNDLE_KEY
from plone import api
from plone.dexterity.utils import createContentInContainer
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


logger = logging.getLogger('opengever.setup.constructor')


class InvalidType(Exception):
    pass


class ConstructorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

        self.site = api.portal.get()
        self.ttool = api.portal.get_tool(u'portal_types')

    def has_translated_title(self, fti):
        return ITranslatedTitle.__identifier__ in fti.behaviors

    def __iter__(self):
        for item in self.previous:
            portal_type = item[u'_type']

            parent_guid = item.get(u'parent_guid')
            if parent_guid:
                context = self.bundle.item_by_guid[parent_guid][u'_object']
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

                obj = createContentInContainer(
                    context, portal_type, **title_args)
                parent_path = '/'.join(context.getPhysicalPath())
            except ValueError as e:
                logger.warning(
                    u'Could not create object at {} with guid {}. {}'.format(
                        parent_path, item['guid'], e.message))
                continue

            # build path relative to plone site
            item[u'_path'] = '/'.join(obj.getPhysicalPath()[2:])
            item[u'_object'] = obj

            yield item
