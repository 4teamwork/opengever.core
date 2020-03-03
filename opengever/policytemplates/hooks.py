from mrbob.hooks import to_boolean
from mrbob.hooks import to_integer
from mrbob.hooks import validate_choices
from opengever.base.interfaces import DEFAULT_FORMATTER
from opengever.base.interfaces import DEFAULT_PREFIX_STARTING_POINT
from opengever.document.interfaces import PRESERVED_AS_PAPER_DEFAULT
from opengever.dossier.interfaces import DEFAULT_DOSSIER_DEPTH
from opengever.mail.interfaces import DEFAULT_MAIL_MAX_SIZE
from opengever.repository.interfaces import DEFAULT_REPOSITORY_DEPTH
from pkg_resources import resource_filename
import os
import shutil


def init_defaults(configurator, question):
    """Could not find another hook to init stuff, so we abuse the first
    question."""

    configurator.defaults.update({
        'setup.maximum_dossier_depth': DEFAULT_DOSSIER_DEPTH,
        'setup.maximum_mail_size': DEFAULT_MAIL_MAX_SIZE,
        'setup.maximum_repository_depth': DEFAULT_REPOSITORY_DEPTH,
        'setup.preserved_as_paper': PRESERVED_AS_PAPER_DEFAULT,
        'setup.reference_number_formatter': DEFAULT_FORMATTER,
        'setup.reference_prefix_starting_point': DEFAULT_PREFIX_STARTING_POINT,
    })


def post_package_name(configurator, question, answer):
    configurator.defaults.update({
        'package.url': 'https://github.com/4teamwork/opengever.{}'.format(
            answer),
        'adminunit.abbreviation': answer,
        'adminunit.id': answer,
    })
    configurator.variables['package.name_capitalized'] = answer.capitalize()
    configurator.variables['package.name_upper'] = answer.upper()
    return answer


def post_package_title(configurator, question, answer):
    configurator.defaults.update({
        'adminunit.title': answer,
    })
    return answer


def post_adminunit_title(configurator, question, answer):
    configurator.defaults.update({
        'orgunit.title': answer,
    })
    return answer


def post_adminunit_abbreviation(configurator, question, answer):
    configurator.defaults.update({
        'adminunit.id': answer.lower(),
        'deployment.ldap_ou': '{}'.format(answer.capitalize()),
        'deployment.rolemanager_group': '{}_admins'.format(answer),
        'deployment.records_manager_group': '{}_admins'.format(answer),
        'deployment.archivist_group': '{}_admins'.format(answer),
        'orgunit.users_group': '{}_users'.format(answer),
        'orgunit.inbox_group': '{}_inbox'.format(answer),
        'orgunit.id': answer.lower()
    })
    return answer


def post_adminunit_id(configurator, question, answer):
    configurator.variables['adminunit.ac_cookie_name'] = answer.replace('-', '_')
    return answer


def post_base_domain(configurator, question, answer):
    configurator.defaults.update({
        'adminunit.site_url': 'https://{}'.format(answer),
        'adminunit.public_url': 'https://{}'.format(answer),
        'deployment.mail_domain': answer,
        'deployment.mail_from_address': 'info@{}'.format(answer),
    })
    return answer


def post_nof_templates(configurator, question, answer):
    if not answer:
        return ''

    answer = to_integer(configurator, question, answer)
    configurator.variables['include_templates'] = bool(answer)
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


def post_preserved_as_paper(configurator, question, answer):
    if not answer:
        return ''

    answer = to_boolean(configurator, question, str(answer))
    if answer == PRESERVED_AS_PAPER_DEFAULT:
        return ''

    return answer


def post_render(configurator):
    has_templates = configurator.variables['include_templates']
    has_meeting = configurator.variables['setup.enable_meeting_feature']
    has_workspace = configurator.variables['setup.workspace']

    package_name = configurator.variables['package.name']
    profiles_path = os.path.join(
        configurator.target_directory,
        'opengever.{}'.format(package_name),
        'opengever', package_name, 'profiles')

    content_path = os.path.join(
        profiles_path,
        'default_content',
        'opengever_content')

    if has_meeting:
        _copy_sablon_templates(content_path)

    else:
        _delete_committees_configuration(content_path)

        if not has_templates:
            _delete_templates_files(configurator, content_path)

    if not has_workspace:
        _delete_workspaces_content_profile(profiles_path)


def _delete_templates_files(configurator, content_path):
    os.remove(os.path.join(content_path, '02-templates.json'))
    os.remove(os.path.join(content_path, 'templates/.gitignore'))
    os.rmdir(os.path.join(content_path, 'templates'))


def _delete_committees_configuration(content_path):
    os.remove(os.path.join(content_path, '03_committees.json'))


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


def _delete_workspaces_content_profile(profiles_path):
    os.remove(os.path.join(profiles_path, 'workspaces_content'))
