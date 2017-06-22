from ftw.mail.utils import get_header
from opengever.base.browser.helper import get_css_class
from opengever.base.utils import escape_html
from opengever.base.utils import get_hostname
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from opengever.tabbedview import _
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import ram
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces._tools import IMemberData
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate


def org_unit_title_helper(item, value):
    return item.get_issuing_org_unit().label()


def display_org_unit_title_condition():
    """A helper for hiding the org-unit title from a task listing if we
    have a single org-unit setup (it would be the same all the time).
    """
    return ogds_service().has_multiple_org_units()


def task_id_checkbox_helper(item, value):
    """ Checkbox helper based on tasks id attribute
    """

    attrs = {
        'type': 'checkbox',
        'class': 'noborder selectable',
        'name': 'task_ids:list',
        'id': item.task_id,
        'value': item.task_id,
        'title': 'Select %s' % item.title,
    }

    return '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                      for k, v in sorted(attrs.items())])


def author_cache_key(m, i, author):
    """Cache key that discriminates on the user ID of the provided user
    (Plone user or string), and the hostname.

    The hostname is required because this cache key is used to cache generated
    URLs, which are dependent on the hostname that is used to access the
    system (might be localhost + SSH tunnel).
    """
    hostname = get_hostname(getRequest())
    if IPropertiedUser.providedBy(author) or IMemberData.providedBy(author):
        userid = author.getId()
    else:
        userid = author
    return (userid, hostname)


@ram.cache(author_cache_key)
def readable_ogds_author(item, author):
    if getattr(item, 'portal_type', None) == 'ftw.mail.mail':
        if getattr(item, 'msg', None):
            # Object
            author = get_header(item.msg, 'From')
        else:
            # Brain
            author = item.document_author

    if not isinstance(author, unicode):
        if author is not None:
            author = author.decode('utf-8')
        else:
            author = ''

    return Actor.lookup(author).get_label()


@ram.cache(author_cache_key)
def readable_ogds_user(item, userid):
    if not isinstance(userid, unicode):
        if userid is not None:
            userid = userid.decode('utf-8')
        else:
            userid = ''

    return Actor.user(userid).get_label()


@ram.cache(author_cache_key)
def linked_ogds_author(item, author):
    return Actor.lookup(author).get_link()


def linked_containing_subdossier(item, value):
    subdossier_title = item.containing_subdossier
    if not subdossier_title:
        return ''

    if ICatalogBrain.providedBy(item):
        url_method = item.getURL
    else:
        url_method = item.absolute_url

    url = "{}/redirect_to_parent_dossier".format(url_method())
    title = escape_html(subdossier_title)

    link = '<a href="{}" title="{}" class="subdossierLink">{}</a>'.format(
        url, title, title)
    return link


def linked(item, value):
    """Takes an item (object or brain) and returns a HTML snippet that
    contains a link to the item, it's icon and breadcrumbs in the tooltip.
    """

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    # Determine URL method and UID
    url_method = lambda: '#'
    if hasattr(item, 'getURL'):
        url_method = item.getURL
        uid = item.UID
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
        uid = IUUID(item)

    # Construct CSS class
    css_class = get_css_class(item)

    # Make sure all data used in the HTML snippet is properly escaped
    value = escape_html(value)

    link = '<a class="rollover-breadcrumb %s" href="%s" data-uid="%s">%s</a>' % (
        css_class, url_method(), uid, value)

    wrapper = '<span class="linkWrapper">%s</span>' % link
    return wrapper


def linked_sql_object(item, value):
    """Tabbedview helper for sqlobjects, wich renders a link to the
    sqlobjects url.

    The given item must provide a `get_url` getter.
    """
    return u'<a href="{}">{}</a>'.format(item.get_url(), escape_html(value))


def document_with_icon(item, value):
    value = escape_html(value)
    icon = u'<span class="{}"></span><span>{}</span>'.format(
        get_css_class(item), value)
    return icon


def linked_document(item, value):
    """Tabbedview helper wich returns a rendered link for the a document,
    using the DocumentLinkWidget.
    """

    return DocumentLinkWidget(item).render()


def linked_version_preview(item, value):
    url = "{}/@@bumblebee-overlay-listing?version_id={}".format(
        item.url, item.version)

    showroom_title = translate(
        _('label_showroom_version_title',
            default='Version ${version} of ${timestamp}',
            mapping={'version': item.version, 'timestamp': item.timestamp}),
        context=getRequest()).encode('utf-8')

    data = {
        'url': url,
        'showroom_url': url,
        'showroom_title': showroom_title,
        'title': translate(
            _('label_preview', default='Preview'),
            context=getRequest()).encode('utf-8')
    }

    return """
    <div>
        <a class="showroom-item function-preview-pdf"
           href="{%(url)s}"
           data-showroom-target="%(showroom_url)s"
           data-showroom-title="%(showroom_title)s">%(title)s</a>
    </div>
    """ % data


def readable_date_set_invisibles(item, date):
    if not date or str(date) == '1970/01/01' \
            or str(date) == '1970-01-01 00:00:00':
        return u''
    strftimestring = '%d.%m.%Y'

    if date is None:
        return None
    return date.strftime(strftimestring)


def email_helper(item, value):
    if value:
        return '<a href="mailto:%s">%s</a>' % (value, value)
    else:
        return ''


def boolean_helper(item, value):
    """Helper for displaying a boolean field in human readable form.
    """

    request = getRequest()
    if value:
        return translate('Yes', domain='plone', context=request)

    return translate('No', domain='plone', context=request)


def workflow_state(item, value):
    """Helper which translates the workflow_state in plone domain
    and adds a CSS class to indicate the worflow state.
    """

    normalize = getUtility(IIDNormalizer).normalize
    state = normalize(item.review_state)
    # We use zope.globalrequest because item can be a SQLAlchemy `Task` object
    # which doesn't have a request
    request = getRequest()
    return """<span class="wf-%s">%s</span>""" % (
        state, translate(value, domain='plone', context=request))


def queue_view_helper(item, value):
    site = getSite()
    return """<a href='%s/jobs_view?queue=%s'>%s</a>""" % (
        site.absolute_url(), value, value)


def external_edit_link(item, value):
    """Return a link Tag to the checkout_documents view,
    with the external_edit mode selected """
    if item.portal_type != 'opengever.document.document':
        return ''
    if hasattr(item, 'getURL'):
        url = item.getURL()
    elif hasattr(item, 'absolute_url'):
        url = item.absolute_url()
    else:
        return ''

    url = '%s/editing_document' % url

    return '<a id="%s" title="%s" href="%s" class="function-edit"></a>' % (
        item.id,
        getSite().translate(
            'checkout_and_edit', domain="opengever.tabbedview"),
        url)


def translated_string(domain='plone'):
    domain = domain

    def _translate(item, value):
        return translate(
            value, context=getRequest(), domain=domain)
    return _translate


def escape_html_transform(item, value):
    if value is None:
        return value
    return escape_html(value)
