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

        policy = input(
            "What policy type do you want to create?\n"
            " 1: GEVER (Compose)\n"
            " 2: Teamraum (Compose)\n"
            " 3: GEVER (Buildout)\n"
            " 4: Teamraum (Buildout)\n"
        )
        if policy == 1:
            template = 'opengever.policytemplates:compose_template'
            init_file = 'opengever/policytemplates/gever.ini'
        elif policy == 2:
            template = 'opengever.policytemplates:compose_template'
            init_file = 'opengever/policytemplates/teamraum.ini'
        elif policy == 3:
            template = 'opengever.policytemplates:policy_template'
            init_file = 'opengever/policytemplates/gever.ini'
        elif policy == 4:
            template = 'opengever.policytemplates:policy_template'
            init_file = 'opengever/policytemplates/teamraum.ini'
        else:
            print('Invalid choice')
            sys.exit()

        args.append(template)
        args.append('--config={}'.format(init_file))
        if 'opengever.core.testserver.OPENGEVER_TESTSERVER' in remainder:
            remainder.remove('opengever.core.testserver.OPENGEVER_TESTSERVER')
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
