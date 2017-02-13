import pkg_resources
import sys

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use: ./bin/zopepy ./src/profile-merge-tool/merge.py'
    sys.exit(1)


from collections import defaultdict
from lxml import etree
from operator import itemgetter
from operator import methodcaller
from path import Path
from plone.memoize import instance
from pprint import pprint
import os
import re


def step(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return execute_step(message, func, *args, **kwargs)
        return wrapper
    return decorator


def execute_step(message, func, *args, **kwargs):
    print '\xf0\x9f\x94\xa7 ', message
    try:
        returnvalue = func(*args, **kwargs)
    except:
        print '\xf0\x9f\x92\xa5'
        raise
    else:
        print '\xe2\x9c\x94 \xf0\x9f\x8d\xba'
        print ''
        return returnvalue


class MergeTool(object):

    def __init__(self):
        self.here_dir = Path(__file__).parent.abspath()
        self.buildout_dir = Path(__file__).parent.parent.parent.abspath()
        assert self.buildout_dir.joinpath('bootstrap.py'), \
            'Could not find buildout root.'
        self.opengever_dir = self.buildout_dir.joinpath('opengever')
        self.og_core_profile_dir = self.opengever_dir.joinpath(
            'core', 'profiles', 'default')

    def __call__(self):
        self.create_opengever_core_profile()
        self.list_old_profiles()
        self.migrate_dependencies()
        self.migrate_standard_xmls()
        self.migrate_mailhost()
        self.migrate_workflows()
        self.migrate_types()
        self.validate_no_leftovers()
        self.migrate_hook_registrations()
        self.install_the_new_profile()

    @step('Create opengever.core Generic Setup profile.')
    def create_opengever_core_profile(self):
        source = self.here_dir.joinpath('opengever-core')
        target = self.opengever_dir.joinpath('core')
        cmd = 'cp -r {}/* {}'.format(source, target)
        print '   >', cmd
        os.system(cmd)

    @step('These profiles will be merged in this order:')
    def list_old_profiles(self):
        for profile in self.profiles_to_migrate:
            print '  ', profile

    @step('Migrate GS dependencies into opengever.core profile.')
    def migrate_dependencies(self):
        # Migrate dependencies according to recursive dependency lookup,
        # skipping merged profiles.
        # We do not remove dependencies from old profiles since we will
        # no longer install them and we need the dependencies for upgrade
        # step ordering.
        target_metadata = self.og_core_profile_dir.joinpath('metadata.xml')
        with target_metadata.open() as fio:
            target_doc = etree.parse(fio)

        dependencies_node = target_doc.xpath('//dependencies')[0]
        dependencies_node.text = '\n' + ' ' * 8
        for profile in self.read_dependencies('opengever.policy.base:default'):
            if profile in self.profiles_to_migrate:
                # do not migrate dependency to migrated profiles (og.task, ..)
                continue
            node = etree.SubElement(dependencies_node, 'dependency')
            node.text = 'profile-' + profile
            node.tail = dependencies_node.text

        node.tail = '\n' + ' ' * 4
        target_metadata.write_bytes(etree.tostring(target_doc))

    def migrate_standard_xmls(self):
        standard_xmls = (
            'actions.xml',
            'browserlayer.xml',
            'catalog.xml',
            'controlpanel.xml',
            'cssregistry.xml',
            'jsregistry.xml',
            'portlets.xml',
            'properties.xml',
            'propertiestool.xml',
            'registry.xml',
            'repositorytool.xml',
            'rolemap.xml',
            'skins.xml',
            'types.xml',
            'viewlets.xml',
            'workflows.xml',
        )

        map(lambda name: execute_step(
            'Migrating {}'.format(name), self.standard_migrate_xml, name),
            standard_xmls)

    @step('Migrate mailhost.xml')
    def migrate_mailhost(self):
        # There is only one mailhost.xml.
        # Since everything is in the XML roo tnode, we cannot use
        # standard_migrate_xml.
        xmls = self.find_file_in_profiles_to_migrate('mailhost.xml')
        assert len(xmls) == 1, 'Expected exactly 1 mailhost.xml, got {!r}'.format(
            xmls)
        xmls[0].move(self.og_core_profile_dir)

    @step('Migrate workflows')
    def migrate_workflows(self):
        seen = []
        for path in reduce(list.__add__,
                           map(methodcaller('glob', '*/definition.xml'),
                               self.find_dir_in_profiles_to_migrate('workflows'))):
            wf_name = str(path.parent.name)
            if wf_name in seen:
                raise ValueError(
                    'Workflow definition for {!r} appears twice'.format(wf_name))
            seen.append(wf_name)

            target = self.og_core_profile_dir.joinpath(
                path.relpath(path.parent.parent.parent))
            target.parent.makedirs()
            path.move(target)
            path.parent.rmdir()
            path.parent.parent.rmdir_p()

    @step('Migrate types')
    def migrate_types(self):
        sources_by_filename = defaultdict(list)
        for path in reduce(list.__add__,
                           map(methodcaller('glob', '*.xml'),
                               self.find_dir_in_profiles_to_migrate('types'))):
            sources_by_filename[str(path.name)].append(path)


        # opengever.tasktemplates:default is installed BEFORE
        # opengever.meeting:default, but tasktemplates customizes
        # meetingdossier before it is even installed.
        # In order to fix such issues, we reorder some FTIs manually here:
        # move the primary XML to position 0
        for relpath in (
                'meeting/profiles/default/types/opengever.meeting.meetingdossier.xml',
        ):
            path = self.opengever_dir.joinpath(relpath)
            filename = str(path.name)
            sources_by_filename[filename].remove(path)
            sources_by_filename[filename].insert(0, path)


        target_types_dir = self.og_core_profile_dir.joinpath('types').mkdir()
        for filename, sources in sources_by_filename.items():
            sources = sources[:]  # copy
            target_path = target_types_dir.joinpath(filename)
            source_path = sources.pop(0)
            source_path.move(target_path)
            source_path.parent.rmdir_p()

            if not sources:
                continue

            with target_path.open('r') as fio:
                target_doc = etree.parse(fio)

            for source_path in sources:
                with source_path.open('r') as fio:
                    source_doc = etree.parse(fio)

                self.add_source_comment(target_doc.getroot(), source_path)
                for node in source_doc.getroot().getchildren():
                    if isinstance(node, etree._Comment) or \
                       node.tag == 'action':
                        target_doc.getroot().append(node)

                    elif node.tag == 'property' and \
                         node.attrib.get('name') == 'allowed_content_types':
                        if node.attrib.get('purge') not in ('False', 'false'):
                            raise ValueError(
                                'Error merging FTIs: '
                                'cannot merge <property> when not purging. '
                                'Attrs: {!r}'.format(node.attrib))
                        target_node = target_doc.xpath(
                            '//property[@name="allowed_content_types"]')
                        if len(target_node) != 1:
                            raise ValueError(
                                'Couldnt find 1 <property '
                                'name="allowed_content_types"> in {}'.format(
                                    target_path))

                        target_node, = target_node
                        map(target_node.append, node.getchildren())

                    else:
                        raise ValueError(
                            'Error merging FTIs: <{}> unsupported in {}.\n{!r}'
                            .format(node.tag, source_path,
                                    sources_by_filename[filename]))

                target_path.write_bytes(etree.tostring(target_doc))
                source_path.unlink().parent.rmdir_p()

    @step('Check for leftovers in old profiles')
    def validate_no_leftovers(self):
        errors = False

        for profile in self.profiles_to_migrate:
            for item in self.profile_path(profile).listdir():
                if item.name == 'metadata.xml':
                    continue
                if not errors:
                    print '   ERROR: leftovers found:'
                    errors = True

                print '  ', profile.ljust(35), item.isdir() and 'D' or ' ', item.name

        assert not errors, 'Should not have any leftovers'

    @step('Migrate hook registrations.')
    def migrate_hook_registrations(self):
        handler_by_profile = {}

        for path in self.opengever_dir.walkfiles('*.zcml'):
            with path.open() as fio:
                doc = etree.parse(fio)

            changes = False
            for node in doc.xpath('//*[local-name()="hook"]'):
                profile = node.attrib.get('profile')
                if profile not in self.profiles_to_migrate:
                    continue
                handler = node.attrib.get('handler')
                assert handler.startswith('.')
                package = path.parent.relpath(self.buildout_dir).replace('/', '.')
                handler = package + handler
                handler_by_profile[profile] = handler
                node.getparent().remove(node)
                changes = True

            if changes:
                path.write_bytes(etree.tostring(doc))

        handlers = map(
            itemgetter(1),
            sorted(handler_by_profile.items(),
                   key=lambda item: self.profiles_to_migrate.index(item[0])))

        target_hooks = self.opengever_dir.joinpath('core', 'hooks.py')
        hooks_lines = map(
            lambda handler: 'import {}'.format(handler.rsplit('.', 1)[0]),
            sorted(handlers))
        hooks_lines.extend(['', '', target_hooks.bytes().strip()])
        hooks_lines.extend(map('    {}(site)'.format, handlers))
        target_hooks.write_bytes('\n'.join(hooks_lines) + '\n')

    @step('Install the new profile')
    def install_the_new_profile(self):
        path = self.opengever_dir.joinpath('setup/meta.py')
        code = path.bytes()
        code = code.replace("default=u'opengever.policy.base:default'",
                            "default=u'opengever.core:default'")
        path.write_bytes(code)

    def standard_migrate_xml(self, filename):
        with self.og_core_profile_dir.joinpath(filename).open() as fio:
            target = etree.parse(fio)

        for path in self.find_file_in_profiles_to_migrate(filename):
            with path.open() as fio:
                doc = etree.parse(fio)

            self.add_source_comment(target.getroot(), path)
            map(target.getroot().append, doc.getroot().getchildren())
            path.unlink()

        self.og_core_profile_dir.joinpath(filename).write_bytes(
            etree.tostring(target))


    def find_file_in_profiles_to_migrate(self, filename):
        return filter(methodcaller('isfile'),
                      map(methodcaller('joinpath', filename),
                          map(self.profile_path, self.profiles_to_migrate)))

    def find_dir_in_profiles_to_migrate(self, filename):
        return filter(methodcaller('isdir'),
                      map(methodcaller('joinpath', filename),
                          map(self.profile_path, self.profiles_to_migrate)))

    @property
    @instance.memoize
    def profiles_to_migrate(self):
        result = []
        for profile in self.read_dependencies('opengever.policy.base:default'):
            if not profile.startswith('opengever.'):
                continue
            elif profile in result:
                print '   WARNING: skipping duplicate profile', profile
            else:
                result.append(profile)
        return result

    def profile_path(self, profile):
        profile = re.sub('^profile-', '', profile)
        return (self.buildout_dir
                .joinpath(*profile.split(':')[0].split('.'))
                .joinpath('profiles', profile.split(':')[1])).abspath()

    def recursive_dependencies(self, profile):
        return map(self.read_dependencies, self.read_dependencies(profile))

    @instance.memoize
    def read_dependencies(self, profile):
        metadata_xml_path = (self.profile_path('opengever.policy.base:default')
                             .joinpath('metadata.xml'))
        if not metadata_xml_path.isfile() and metadata_xml_path.parent.isdir():
            return []

        with metadata_xml_path.open() as fio:
            doc = etree.parse(fio)

        result = []
        for node in doc.xpath('//dependency'):
            result.append(re.sub('^profile-', '', node.text.strip()))

        return result

    def add_source_comment(self, node, path):
        if node.getchildren():
            node.getchildren()[-1].tail = '\n\n\n    '
        else:
            node.text = '\n\n    '

        comment = etree.Comment('merged from {}'.format(
            path.relpath(self.buildout_dir)))
        comment.tail = '\n    '
        node.append(comment)


if __name__ == '__main__':
    MergeTool()()
