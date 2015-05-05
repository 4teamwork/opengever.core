from mrbob.hooks import to_boolean
from mrbob.hooks import to_integer
from mrbob.hooks import validate_choices
from opengever.base.interfaces import DEFAULT_FORMATTER
from opengever.base.interfaces import DEFAULT_PREFIX_STARTING_POINT
from opengever.document.interfaces import PRESERVED_AS_PAPER_DEFAULT
from opengever.dossier.interfaces import DEFAULT_DOSSIER_DEPTH
from opengever.mail.interfaces import DEFAULT_MAIL_MAX_SIZE
from opengever.repository.interfaces import DEFAULT_REPOSITORY_DEPTH
import os


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
        'package.name': answer,
        'adminunit.id': answer,
        'deployment.ldap_ou': 'OpenGever{}'.format(answer.capitalize()),
        'deployment.rolemanager_group': 'og_{}_leitung'.format(answer),
        'orgunit.users_group': 'og_{}_benutzer'.format(answer),
        'orgunit.inbox_group': 'og_{}_sekretariat'.format(answer),
        'orgunit.id': answer
    })
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
    if not configurator.variables['include_templates']:
        _delete_templates_files(configurator)


def _delete_templates_files(configurator):
    package_name = configurator.variables['package.name']
    content_path = os.path.join(
        configurator.target_directory,
        'opengever.{}'.format(package_name),
        'opengever',
        package_name,
        'profiles',
        'default_content',
        'opengever_content')

    os.remove(os.path.join(content_path, '02-templates.json'))
    os.rmdir(os.path.join(content_path, 'templates'))
