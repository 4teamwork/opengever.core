import argparse
import mrbob.cli
import sys


class CreatePolicyCLI(object):
    """Command Line Interface that will be available through the
    bin/create-policy script in the development buildout directory.

    For now it's a simple wrapper around bin/mrbob.
    """

    def __init__(self, args):
        self.args = args

    def run(self):
        options, remainder = self._parse_args()
        args = []

        target_dir = 'src/'
        args.append('-O')
        args.append(target_dir)

        template = 'opengever.policytemplates:policy_template'
        args.append(template)

        if remainder:
            args.extend(remainder)

        sys.exit(mrbob.cli.main(args=args))

    def _parse_args(self):
        prog = self.args.pop(0)

        # Top level parser
        parser = argparse.ArgumentParser(prog=prog)

        return parser.parse_known_args(args=self.args)


def main():
    CreatePolicyCLI(sys.argv).run()


if __name__ == '__main__':
    main()
