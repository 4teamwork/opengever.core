from mrbob.hooks import to_integer
import os


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
    answer = to_integer(configurator, question, answer)
    configurator.variables['include_templates'] = bool(answer)
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
