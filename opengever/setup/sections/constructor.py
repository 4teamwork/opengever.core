from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from plone import api
from plone.dexterity.utils import createContentInContainer
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
        self.item_by_guid = self.transmogrifier.item_by_guid

        self.site = api.portal.get()
        self.ttool = api.portal.get_tool(u'portal_types')

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
                obj = createContentInContainer(
                    context, portal_type,
                    title_de=item.get(u'title_de'),
                    title_fr=item.get(u'title_fr'),
                    title=item.get(u'title'))
                parent_path = '/'.join(context.getPhysicalPath())
            except ValueError as e:
                logger.warning(
                    u'Could not create object at {} with guid {}. {}'.format(
                        parent_path, item['guid'], e.message))
                continue

            item[u'_path'] = '/'.join(obj.getPhysicalPath())
            item[u'_object'] = obj

            yield item
