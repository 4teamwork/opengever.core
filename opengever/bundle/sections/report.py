from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.pathfinder import PathFinder
from opengever.bundle.report import ASCIISummaryBuilder
from opengever.bundle.report import DataCollector
from opengever.bundle.report import XLSXReportBuilder
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import os
import tempfile


log = logging.getLogger('opengever.bundle.report')
log.setLevel(logging.INFO)


class ReportSection(object):
    """Create import reports for the current OGGBundle.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

    def __iter__(self):
        for item in self.previous:
            yield item

        log.info("Creating import reports...")

        report_data = DataCollector(self.bundle)()
        self.bundle.report_data = report_data

        self.build_ascii_summary(report_data)
        self.build_xlsx_report(report_data)

    def build_ascii_summary(self, report_data):
        summary = ASCIISummaryBuilder(report_data).build()
        log.info('\n\n%s\n' % summary)

    def build_xlsx_report(self, report_data):
        try:
            report_path = os.path.join(PathFinder().var, 'report.xlsx')
        except RuntimeError:
            # During tests
            tmp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.xlsx')
            tmp_file.close()
            report_path = tmp_file.name

        xlsx_builder = XLSXReportBuilder(report_data)
        xlsx_builder.build_and_save(report_path)
