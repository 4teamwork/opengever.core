from mrbob.hooks import to_boolean
from mrbob.hooks import to_integer
from mrbob.hooks import validate_choices
from opengever.base.interfaces import DEFAULT_FORMATTER
from opengever.base.interfaces import DEFAULT_PREFIX_STARTING_POINT
from opengever.dossier.interfaces import DEFAULT_DOSSIER_DEPTH
from opengever.mail.interfaces import DEFAULT_MAIL_MAX_SIZE
from opengever.repository.interfaces import DEFAULT_REPOSITORY_DEPTH
from pkg_resources import resource_filename
import os
import shutil

IGNORED_QUESTIONS = {
    'teamraum': [
        'orgunit.inbox_group'
        'deployment.rolemanager_group',
        'deployment.records_manager_group',
        'deployment.archivist_group',
        'setup.enable_activity_feature',
        'setup.enable_meeting_feature',
        'setup.enable_docproperty_feature',
        'setup.nof_templates',
        'setup.maximum_repository_depth',
        'setup.reference_prefix_starting_point',
        'setup.reference_number_formatter',
        'setup.maximum_dossier_depth',
        'setup.preserved_as_paper',
        'setup.enable_private_folder',
        'setup.dossier_templates',
        'setup.ech0147_export',
        'setup.ech0147_import',
        'setup.officeatwork',
        'setup.repositoryfolder_documents_tab',
        'setup.repositoryfolder_tasks_tab',
        'setup.repositoryfolder_proposals_tab',
        'setup.bumblebee_auto_refresh',
        ],
    'gever': [
        'deployment.workspace_administrators_group',
        'deployment.workspace_creators_group',
        'deployment.workspace_users_group',
        'base.apps_endpoint_url',
        ]
    }

IGNORED_DIRECTORIES = {
    'teamraum': ['default_content'],
    'gever': ['workspaces_content']
    }

IGNORED_FILES = {
    'teamraum': ['hooks.py.bob'],
    'gever': []
    }

VARIABLE_VALUES = {
    'teamraum': {
        'setup.geverui': True,
        'setup.bumblebee_auto_refresh': True,
        'setup.enable_activity_feature': True,
        },
    'gever': {}
    }

DEFAULT_VALUES = {
    'teamraum': {
        'adminunit.title': 'Teamraum',
        'adminunit.abbreviation': 'tr',
        'adminunit.id': 'tr',
        'setup.maximum_mail_size': DEFAULT_MAIL_MAX_SIZE,
    },
    'gever': {
        'setup.maximum_dossier_depth': DEFAULT_DOSSIER_DEPTH,
        'setup.maximum_mail_size': DEFAULT_MAIL_MAX_SIZE,
        'setup.maximum_repository_depth': DEFAULT_REPOSITORY_DEPTH,
        'setup.reference_number_formatter': DEFAULT_FORMATTER,
        'setup.reference_prefix_starting_point': DEFAULT_PREFIX_STARTING_POINT,
    }
}


def policy_type(configurator):
    return configurator.variables.get('policy.type')


def initialize(configurator, question):
    """Could not find another hook to init stuff, so we abuse the first
    question."""
    # For convenience we store is_teamraum and is_gever variables
    configurator.variables['is_teamraum'] = configurator.variables.get('policy.type') == 'teamraum'
    configurator.variables['is_gever'] = configurator.variables.get('policy.type') == 'gever'
    init_defaults(configurator)
    init_values(configurator)
    filter_questions(configurator)
    add_ignored_directories(configurator)
    add_ignored_files(configurator)


def filter_questions(configurator):
    to_remove = []
    for question in configurator.questions:
        if question.name in IGNORED_QUESTIONS[policy_type(configurator)]:
            to_remove.append(question)
    for question in to_remove:
        configurator.questions.remove(question)


def add_ignored_directories(configurator):
    configurator.ignored_directories.extend(
        IGNORED_DIRECTORIES[policy_type(configurator)]
        )


def add_ignored_files(configurator):
    configurator.ignored_files.extend(IGNORED_FILES[policy_type(configurator)])


def init_defaults(configurator):
    configurator.defaults.update(DEFAULT_VALUES[policy_type(configurator)])


def init_values(configurator):
    configurator.variables.update(VARIABLE_VALUES[policy_type(configurator)])


def update_defaults(configurator, new_defaults):
    """We only update the defaults if they are not set for the given policy
    """
    policy_defaults = DEFAULT_VALUES[policy_type(configurator)]
    for key, value in new_defaults.items():
        if key in policy_defaults:
            continue
        configurator.defaults[key] = value


def post_package_name(configurator, question, answer):
    domain_default = '{}.{}.ch'.format(
        answer,
        'onegovgever' if configurator.variables['is_gever'] else 'teamraum'
        )
    new_defaults = {
        'package.url': 'https://github.com/4teamwork/opengever.{}'.format(
            answer),
        'adminunit.abbreviation': answer,
        'adminunit.id': answer,
        'base.domain': domain_default,
    }
    update_defaults(configurator, new_defaults)
    configurator.variables['package.name_capitalized'] = answer.capitalize()
    configurator.variables['package.name_upper'] = answer.upper()
    return answer


def post_package_title(configurator, question, answer):
    update_defaults(configurator, {
        'adminunit.title': answer
        })
    return answer


def post_adminunit_title(configurator, question, answer):
    update_defaults(configurator, {
        'orgunit.title': answer
        })
    if configurator.variables['is_teamraum']:
        # Teamraum does not support more than one orgunit, so there is
        # no reason to have a discrepency between orgunit and adminunit
        configurator.variables.update({
            'orgunit.title': answer
            })
    return answer


def post_adminunit_abbreviation(configurator, question, answer):
    new_defaults = {
        'adminunit.id': answer.lower(),
        'deployment.ldap_ou': '{}'.format(answer.capitalize()),
        'deployment.rolemanager_group': '{}_admins'.format(answer),
        'deployment.records_manager_group': '{}_admins'.format(answer),
        'deployment.archivist_group': '{}_admins'.format(answer),
        'orgunit.users_group': '{}_users'.format(answer),
        'orgunit.inbox_group': '{}_inbox'.format(answer),
        'orgunit.id': answer.lower()
    }
    update_defaults(configurator, new_defaults)
    if configurator.variables['is_teamraum']:
        # Teamraum does not support more than one orgunit, so there is
        # no reason to have a discrepency between orgunit and adminunit
        configurator.variables.update({
            'orgunit.id': answer.lower()
            })
    return answer


def post_adminunit_id(configurator, question, answer):
    configurator.variables['adminunit.ac_cookie_name'] = answer.replace('-', '_')
    configurator.variables['adminunit.id_capitalized'] = answer.capitalize()
    configurator.variables['adminunit.id_upper'] = answer.upper()
    return answer


def post_base_domain(configurator, question, answer):
    new_defaults = {
        'adminunit.site_url': 'https://{}'.format(answer),
        'adminunit.public_url': 'https://{}'.format(answer),
        'deployment.mail_domain': answer,
        'deployment.mail_from_address': 'info@{}'.format(answer),
        'base.apps_endpoint_url': 'https://{}/api/apps'.format(answer),
    }
    update_defaults(configurator, new_defaults)
    return answer


def post_nof_templates(configurator, question, answer):
    if not answer:
        return ''

    answer = to_integer(configurator, question, answer)

    if not bool(answer):
        configurator.ignored_directories.append('templates')
        configurator.ignored_files.append('02-templates.json.bob')

    return answer


def post_maximum_repository_depth(configurator, question, answer):
    if not answer:
        return ''

    answer = to_integer(configurator, question, answer)
    if answer == DEFAULT_REPOSITORY_DEPTH:
        return ''

    return answer


def post_reference_prefix_starting_point(configurator, question, answer):
    if answer == DEFAULT_PREFIX_STARTING_POINT:
        return ''

    return answer


def post_reference_number_formatter(configurator, question, answer):
    if not answer:
        return ''

    answer = validate_choices(configurator, question, answer)
    if answer == DEFAULT_FORMATTER:
        return ''

    return answer


def post_maximum_dossier_depth(configurator, question, answer):
    if not answer:
        return ''

    answer = to_integer(configurator, question, answer)
    if answer == DEFAULT_DOSSIER_DEPTH:
        return ''

    return answer


def post_maximum_mail_size(configurator, question, answer):
    if not answer:
        return ''

    answer = to_integer(configurator, question, answer)
    if answer == DEFAULT_MAIL_MAX_SIZE:
        return ''

    return answer


def post_enable_meeting_feature(configurator, question, answer):
    answer = to_boolean(configurator, question, answer)
    if not answer:
        configurator.ignored_files.append('03_committees.json.bob')
    return answer


def post_render(configurator):
    if configurator.variables['is_teamraum']:
        return
    has_meeting = configurator.variables['setup.enable_meeting_feature']

    package_name = configurator.variables['package.name']
    adminunit_id = configurator.variables['adminunit.id']
    profiles_path = os.path.join(
        configurator.target_directory,
        'opengever.{}'.format(package_name),
        'opengever', package_name, adminunit_id, 'profiles')

    content_path = os.path.join(
        profiles_path,
        'default_content',
        'opengever_content')

    if has_meeting:
        _copy_sablon_templates(content_path)


def _copy_sablon_templates(content_path):
    templates_path = os.path.join(content_path, 'templates')

    for path in _get_sablon_template_paths():
        shutil.copy(path, templates_path)


def _get_sablon_template_paths():
    paths = []
    filenames = ['protokoll.docx',
                 'protokollauszug.docx',
                 'traktandenliste.docx']

    for filename in filenames:
        paths.append(resource_filename(
            'opengever.examplecontent',
            'profiles/municipality_content/opengever_content/templates/{}'.format(
                filename)))

    return paths
