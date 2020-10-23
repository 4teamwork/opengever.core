import argparse
import os
import sys


READ_ONLY_ENV_VARIABLE = 'GEVER_READ_ONLY_MODE'


def main():
    parser = argparse.ArgumentParser(
        description='Toggle read-only mode of all Zope instances except for '
                    'instance0. Use -i option to toggle instance0 or other '
                    'specific instances.')
    parser.add_argument(
        '-r', '--readonly', action='store_true', default=None,
        help='enable read-only mode regardless of the current state',
        dest='readonly')
    parser.add_argument(
        '-w', '--readwrite', action='store_false', default=None,
        help='disable read-only mode regardless of the current state',
        dest='readonly')
    parser.add_argument(
        '-i', '--instance', action='append', default=None,
        help='toggle read-only mode for the given instance name',
        metavar='INSTANCE', dest='instances')
    options = parser.parse_args()

    confs = get_zope_confs(instances=options.instances)
    if not confs:
        sys.exit('No instance selected.')

    for conf in confs:
        if options.readonly is None:
            if is_readonly(conf):
                disable_readonly(conf)
            else:
                enable_readonly(conf)
        elif options.readonly:
            enable_readonly(conf)
        else:
            disable_readonly(conf)


def is_readonly(conf):
    with open(conf, 'r') as conf_file:
        for line in conf_file:
            if READ_ONLY_ENV_VARIABLE in line:
                return True
    return False


def enable_readonly(conf):
    new_conf = []
    with open(conf, 'r') as conf_file:
        for line in conf_file:
            tokens = line.strip().split()

            if tokens:
                if tokens[0] == READ_ONLY_ENV_VARIABLE:
                    continue
                elif tokens[0] == 'read-only':
                    continue

            new_conf.append(line)

            if line.strip() == '<environment>':
                new_conf.append('{} true\n'.format(READ_ONLY_ENV_VARIABLE))
            elif line.strip() == '<filestorage>':
                new_conf.append('        read-only true\n')
            elif line.strip() == '<zeoclient>':
                new_conf.append('      read-only true\n')
            elif line.strip() == '<relstorage>':
                new_conf.append('        read-only true\n')

    with open(conf, 'w') as conf_file:
        conf_file.writelines(new_conf)

    print('Enabled read-only mode in {}.'.format(conf))


def disable_readonly(conf):
    new_conf = []
    with open(conf, 'r') as conf_file:
        for line in conf_file:
            tokens = line.strip().split()

            if tokens:
                if tokens[0] == READ_ONLY_ENV_VARIABLE:
                    continue
                elif tokens[0] == 'read-only':
                    continue

            new_conf.append(line)

            if line.strip() == '<zeoclient>':
                new_conf.append('      read-only false\n')

    with open(conf, 'w') as conf_file:
        conf_file.writelines(new_conf)

    print('Disabled read-only mode in {}.'.format(conf))


def get_zope_confs(instances=None):
    buildout_dir = os.path.dirname(os.path.dirname(
        os.path.realpath(sys.argv[0])))
    instance_parts = [
        part for part in os.listdir(os.path.join(buildout_dir, 'parts'))
        if part.startswith('instance')
    ]
    selected_parts = [
        part for part in instance_parts
        if instances is None and part != 'instance0'
        or instances and part in instances
    ]
    zope_confs = [
        os.path.join(buildout_dir, 'parts', part, 'etc', 'zope.conf')
        for part in selected_parts
    ]
    return zope_confs


if __name__ == '__main__':
    main()
