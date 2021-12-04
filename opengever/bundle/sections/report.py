from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from datetime import datetime
from opengever.base import advancedjson
from opengever.base.pathfinder import PathFinder
from opengever.bundle.report import ASCIISummaryBuilder
from opengever.bundle.report import DataCollector
from opengever.bundle.report import XLSXMainReportBuilder
from opengever.bundle.report import XLSXValidationReportBuilder
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import os
import tempfile
import transaction


log = logging.getLogger('opengever.bundle.report')
log.setLevel(logging.INFO)

SKIP_REPORT_KEY = 'skip_report'


class ReportSection(object):
    """Create import reports for the current OGGBundle.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        annotations = IAnnotations(transmogrifier)
        self.bundle = annotations[BUNDLE_KEY]
        self.skip_report = annotations.get(SKIP_REPORT_KEY, False)
        self.report_dir = None

    def __iter__(self):
        for item in self.previous:
            yield item

        transaction.commit()
        self.bundle.stats['timings']['migration_finished'] = datetime.now()

        if not self.skip_report:
            log.info("Creating import reports...")
            self.report_dir = self.create_report_dir()

            self.store_as_json(self.bundle.errors, 'errors.json')
            self.store_as_json(self.bundle.stats, 'stats.json')

            report_data = DataCollector(self.bundle)()
            self.bundle.report_data = report_data

            self.build_ascii_summary(self.bundle)
            self.build_xlsx_main_report(self.bundle)
            self.build_xlsx_validation_report(self.bundle)

    def create_report_dir(self):
        """Create a directory to store all import report files.

        In a real invocation, this will be created inside the instance's
        var/ directory (no git-pollution, variable data where it belongs).

        During tests, a temporary directory will be created.
        """
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        dirname = 'import-report-%s' % ts
        try:
            report_dir = os.path.join(PathFinder().var, dirname)
            try:
                os.makedirs(report_dir)
            except OSError:
                # Already exists
                pass
        except RuntimeError:
            # During tests
            report_dir = tempfile.mkdtemp(prefix=dirname)
        return report_dir

    def store_as_json(self, data, filename):
        """Store raw migration stats or errors as JSON files in report dir.
        """
        json_path = os.path.join(self.report_dir, filename)
        with open(json_path, 'w') as json_file:
            advancedjson.dump(data, json_file, sort_keys=True,
                              indent=4, separators=(',', ': '))
        log.info('Stored %s' % json_path)

    def build_ascii_summary(self, bundle):
        summary = ASCIISummaryBuilder(bundle).build()
        log.info('\n\n%s\n' % summary)

    def build_xlsx_main_report(self, bundle):
        report_path = os.path.join(self.report_dir, 'main-report.xlsx')

        builder = XLSXMainReportBuilder(bundle)
        builder.build_and_save(report_path)

    def build_xlsx_validation_report(self, bundle):
        report_path = os.path.join(self.report_dir, 'validation-report.xlsx')

        builder = XLSXValidationReportBuilder(bundle)
        builder.build_and_save(report_path)
