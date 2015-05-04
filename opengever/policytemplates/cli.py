import argparse
import sys


class CreatePolicyCLI(object):
    """Command Line Interface that will by available through the
    bin/create-policy script in the development buildout directory.

    For now it's a simple wrapper around bin/mrbob.
    """

    def __init__(self, args):
        self.args = args

    def run(self):
        options = self._parse_args()
        mrbob = 'bin/mrbob'
        target_dir = 'src/'

        cmdline = mrbob
        if options.verbose:
            cmdline += ' -v'
        cmdline += ' -O %s' % target_dir
        cmdline += ' opengever.policytemplates:policy_template'

        # os.system, because it's friday afternoon and I can't be bothered to
        # figure out subprocess.call()'s usage for the 42nd time. IOW: Fuck it.
        os.system(cmdline)
        print "Done."

    def _parse_args(self):
        prog = sys.argv[0]

        # Top level parser
        parser = argparse.ArgumentParser(prog=prog)

        # Global arguments
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Be very verbose.')

        return parser.parse_args()


def main():
    args = sys.argv
    cli = CreatePolicyCLI(args)
    cli.run()


if __name__ == '__main__':
    main()
