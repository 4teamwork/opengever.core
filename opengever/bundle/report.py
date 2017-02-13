from collections import OrderedDict
from opengever.bundle.loader import BUNDLE_JSON_TYPES
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from plone import api
from zope.annotation import IAnnotations
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DataCollector(object):
    """Collect report data from Plone.
    """

    def __init__(self, bundle):
        self.bundle = bundle

    def __call__(self):
        data = {}
        catalog = api.portal.get_tool('portal_catalog')

        portal_types = BUNDLE_JSON_TYPES.values()
        portal_types.append('ftw.mail.mail')

        for portal_type in portal_types:
            data[portal_type] = []
            log.info("Collecting %s" % portal_type)

            brains = catalog.unrestrictedSearchResults(portal_type=portal_type)
            for brain in brains:
                item_info = self.get_item_info(brain)
                data[portal_type].append(item_info)

        return data

    def get_item_info(self, brain):
        obj = brain.getObject()
        path = '/'.join(obj.getPhysicalPath())
        title = brain.Title
        guid = IAnnotations(obj).get(BUNDLE_GUID_KEY)
        item_info = OrderedDict(
            [('guid', guid), ('path', path), ('title', title)])
        return item_info


class ASCIISummaryBuilder(object):
    """Build a quick ASCII summary of object counts based on report data.
    """

    def __init__(self, report_data):
        self.report_data = report_data

    def build(self):
        report = []
        report.append('Imported objects:')
        report.append('=================')

        for portal_type, items in self.report_data.items():
            line = "%s: %s" % (portal_type, len(items))
            report.append(line)

        return '\n'.join(report)
