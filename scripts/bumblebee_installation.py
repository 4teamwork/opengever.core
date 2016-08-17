"""
Script to reindex and store objects for bumblebee.

To reindex the objects run:

    bin/instance run ./scripts/bumblebee_installation.py -m reindex

To store the objects run:

    bin/instance run ./scripts/bumblebee_installation.py -m reindex

If you have to specify the path to your plone insance
then you can use following parameter:

    -p <path/to/plonesite>

Per default the timestamp wont be resetted. That means, already stored
objects wont be stored again.

If you want to reset the timestamp and store all objects again then you can
define this with the following parameter:

    -r True

For help-information type in the following:

    bin/instance run ./scripts/bumblebee_installation.py -h

"""
from ftw.bumblebee.interfaces import IBumblebeeConverter
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from optparse import OptionParser
from zope.component import getUtility
import logging
import sys
import transaction

# Set global logger to info - this is necessary for the log-outbut with
# bin/instance run.
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

LOG = logging.getLogger('bumblebee-installation')


parser = OptionParser()

parser.add_option("-m", "--mode", dest="mode", type="choice",
                  help="REQUIRED: Specify the upgrade-mode.",
                  choices=['reindex', 'store'],
                  metavar="reindex|store")

parser.add_option("-r", "--reset-timestamp", dest="reset", default=False,
                  action="store_true",
                  help="If set to true, all objects will be reindexed again. "
                       "Otherwise it wont update already stored objects if "
                       "you restart the script",
                  metavar="True|False")

parser.add_option("-p", "--plone", dest="plone_path",
                  help="path to the plonesite.", metavar="path/to/platform")

parser.add_option("-c", "--config", dest="config",
                  help="Zope-Config (do not use this)")


def main(app, argv=sys.argv[1:]):
    options, args = parser.parse_args()

    mode = options.mode.lower() if options.mode else None

    if not options.mode:
        parser.print_help()
        parser.error(
            'Please specify the "mode" with "bin/instance run <yourscript> -m '
            'reindex | store"\n'
            )

    if options.plone_path:
        plone = app.unrestrictedTraverse(options.plone_path)
    else:
        plone = get_first_plone_site(app)

    setup_plone(plone)

    converter = getUtility(IBumblebeeConverter)

    if mode == 'reindex':
        LOG.info("Start indexing objects...")
        converter.reindex()
        return transaction.commit()

    elif mode == 'store':
        LOG.info("Start storing objects...")
        if not options.reset:
            LOG.warning(
                "You started storing without reseting the timestamp. "
                "Already converted objects will be skipped.")

        return converter.store(deferred=True, reset_timestamp=options.reset)

    else:
        parser.print_help()
        parser.error('You entered an invalid mode: {}\n'.format(mode))


if __name__ == '__main__':
    main(app, sys.argv[1:])
