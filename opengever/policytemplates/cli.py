import argparse
import mrbob.cli
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

        args = []
        if options.verbose:
            args.append('-v')

        target_dir = 'src/'
        args.append('-O')
        args.append(target_dir)

        template = 'opengever.policytemplates:policy_template'
        args.append(template)

        sys.exit(mrbob.cli.main(args=args))

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
    CreatePolicyCLI(sys.argv).run()


if __name__ == '__main__':
    main()
