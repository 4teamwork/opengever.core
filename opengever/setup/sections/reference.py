from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberPrefix as PrefixAdapter
from opengever.base.interfaces import IReferenceNumberSettings
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.interface import classProvides, implements
import logging


MAX_LENGTH = 128


class PathFromReferenceNumberSection(object):
    """Creates `_path` entries for items of _type opengever.repository.* based
    on their reference number.

    This sections assumes that:
     - There is *one* item of _type og.repository.repositoryroot
     - All the following items are of _type og.repository.repositoryfolder
     - Items are ordered according to their reference number
     - The parent / child relationships defined by the reference numbers are
       free of contradictions. I.e. there are no repository folders without
       a parent.

    Besides determining the _path, this section also sets the
    `reference_number_prefix` for all repositoryfolder items.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.refnum_mapping = {}
        self.context = transmogrifier.context
        self.normalizer = queryUtility(IURLNormalizer, name="de")
        self.id_normalizer = queryUtility(IIDNormalizer)

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        self.reference_formatter = queryAdapter(
            api.portal.get(), IReferenceNumberFormatter, name=proxy.formatter)

    def __iter__(self):
        self.logger.info("Building paths from reference numbers...")
        for item in self.previous:
            if item.get('_type') == 'opengever.repository.repositoryroot':
                # It's the repository root, just set _path and move on
                item['_path'] = '/{}'.format(item['_repo_root_id'])
                yield item
                continue

            if not item.get('_type') == 'opengever.repository.repositoryfolder':
                self.logger.warn("Skipped unknown item %r" % item)
                yield item
                continue

            refnum = item['reference_number']
            refnum = self.get_reference_number(refnum)

            # We need to keep track of refnums -> paths PER repository
            repo_root_id = item['_repo_root_id']
            if repo_root_id not in self.refnum_mapping:
                self.refnum_mapping[repo_root_id] = {}

            if len(refnum.split('.')) == 1:
                # Top level repository folder
                path = "/%s/%s" % (
                    repo_root_id,
                    self.normalize(
                        item, max_length=MAX_LENGTH, parent_path=repo_root_id))
                self.refnum_mapping[repo_root_id][refnum] = path
            else:
                parent_refnum = refnum[:refnum.rfind('.')]
                if parent_refnum not in self.refnum_mapping[repo_root_id]:
                    raise Exception(
                        "(%s) Parent position for %s does not "
                        "exist!" % (repo_root_id, refnum))

                parent_path = self.refnum_mapping[repo_root_id][parent_refnum]
                path = "%s/%s" % (
                    parent_path,
                    self.normalize(item, max_length=MAX_LENGTH, parent_path=parent_path))
                self.refnum_mapping[repo_root_id][refnum] = path

            item['_path'] = path

            # Now that we used the whole reference number to determine the
            # path, store the rightmost part in 'reference_number_prefix'
            refnum_prefix = refnum.split('.')[-1]
            item['reference_number_prefix'] = refnum_prefix
            yield item
        self.logger.info("...done!")

    def get_reference_number(self, refnum):
        if self.reference_formatter.is_grouped_by_three:
            cl_refnum = refnum.replace('.', '')
            return '.'.join(cl_refnum)
        return refnum

    def normalize(self, item, max_length, parent_path):
        title = item['effective_title']

        if not isinstance(title, unicode):
            title = title.decode('utf-8')

        # Use URLNormalizer to get locale-dependent transcriptions,
        # and IDNormalizer to get lowercased, ID-safe values.
        normalized_id = self.normalizer.normalize(title, max_length=max_length)
        normalized_id = self.id_normalizer.normalize(
            normalized_id, max_length=max_length)

        # Avoid id conflicts
        parent = traverse(self.context, parent_path)
        chooser = INameChooser(parent)
        if not chooser.checkName(normalized_id, parent):
            # namechooser expect the object itself as second paremter, but it's
            # only used for getting the request, therefore we use the parent.
            normalized_id = chooser.chooseName(
                normalized_id, parent)

        return normalized_id


class ResetReferencePrefixMapping(object):
    """Reset the wrong stored referenceprefix value,
    in the reference number child mapping"""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.logger = logging.getLogger(options['blueprint'])

    def __iter__(self):
        for item in self.previous:

            obj = self.context.unrestrictedTraverse(
                item['_path'].lstrip('/'), None)

            if item.get('reference_number_prefix'):
                parent = aq_parent(aq_inner(obj))

                if PrefixAdapter(parent).get_number(obj) != item.get(
                        'reference_number_prefix'):

                    PrefixAdapter(parent).get_child_mapping().pop(
                        PrefixAdapter(parent).get_number(obj))

            yield item
