from App.config import getConfiguration
from path import Path
from plone.memoize import ram
from zope.globalrequest import getRequest
from zope.i18n import translate


def prepare_handlebars_template(path,
                                translations=None,
                                **params):
    """Prepare a handlebars template to be sent to the browser by substituting
    translations and params.

    The handlebars template is rendered on client-side (JavaScript).
    But we often want to substitute strings in the template on the server-side:
    we need to fill in translated strings and settings or other params.

    This function helps simplyfing the job of replacing translation strings and
    params in the template.

    The server-side preparation is based on a simple old-style python string
    substitution. Using a templating language such as page-template or Mako,
    or using the new style string format, will conflict with handlebars' syntax
    and will make the template harder to read because of mixed templating engines
    and syntaxes.

    - Handlebars templates should be stored in the form "templates/xy.html".
    - The template must contain the wrapping <script>-tag.
    - Substitions are old style python, e.g.: %(my_setting)s.
    - Translations are identified by message label, e.g.: %(label_foo)s
    - Params override translations when names clash.

    :param path: The path to the handlebars template.
    :type path: string or :py:class:`path.Path`
    :param translations: A list of message ID objects used in the template.
    :type translations: list of :py:class:`zope.i18nmessageid.Message`
    :param **params: Params to be substituted in the template.
    :returns: The prepared template for including in the response.
    :rtype: string
    """
    request = getRequest()
    for msg in (translations or ()):
        params.setdefault(unicode(msg), translate(msg, context=request))
    return get_handlebars_template(path) % params


def _get_handlebars_template_cache_key(method, path):
    """Calculate cache key for get_handlebars_template for a specific template.

    In development, the template is cached until the template file is modified.
    In production, the template is cached for the process duration.
    Especially while deploying (updating), it is important that a production
    process does not reload components from the file system in order to keep
    code and resources in sync.
    """
    if not getConfiguration().debug_mode:
        return str(path)
    else:
        return '{0!s}-{0.mtime}'.format(Path(path))


@ram.cache(_get_handlebars_template_cache_key)
def get_handlebars_template(path):
    """Return a handlebars template without preparation.

    The template is cached in a ram cache.
    """
    return Path(path).bytes()
