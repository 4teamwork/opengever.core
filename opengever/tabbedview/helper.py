from Products.CMFCore.interfaces._tools import IMemberData
from Products.PluggableAuthService.interfaces.authservice import \
    IPropertiedUser
from datetime import date as dt
from ftw.mail.utils import get_header
from opengever.base.browser.helper import get_css_class
from opengever.ogds.base.interfaces import IContactInformation
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import cgi


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
    if IPropertiedUser.providedBy(author) or IMemberData.providedBy(author):
        return author.getId()
    else:
        return author


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
    if IPropertiedUser.providedBy(author) or IMemberData.providedBy(author):
        author = author.getId()
    info = getUtility(IContactInformation)
    if info.is_user(author) or info.is_contact(
            author) or info.is_inbox(author):
        return info.describe(author)
    else:
        return author


@ram.cache(author_cache_key)
def readable_ogds_user(item, user):
    if not isinstance(user, unicode):
        if user is not None:
            user = user.decode('utf-8')
        else:
            user = ''
    if IPropertiedUser.providedBy(user) or IMemberData.providedBy(user):
        user = user.getId()
    info = getUtility(IContactInformation)
    if info.is_user(user) or info.is_contact(user) or info.is_inbox(user):
        return info.describe(user)
    else:
        return user


@ram.cache(author_cache_key)
def linked_ogds_author(item, author):
    if author:
        if isinstance(author, str):
            author = author.decode('utf-8')
        info = getUtility(IContactInformation)
        if info.is_user(author) or info.is_contact(
            author) or info.is_inbox(author):
            return info.render_link(author)
        else:
            return author
    return ''


def _breadcrumbs_from_item(item):
    """Returns a list of titles for the items parent hierarchy (breadcrumbs).
    `item` can be either a brain or an object.
    """
    breadcrumb_titles = []
    raw_breadcrumb_titles = getattr(item, 'breadcrumb_titles', None)
    if not raw_breadcrumb_titles:
        # Not a brain - get breadcrumbs from the breadcrumbs view
        breadcrumbs_view = getMultiAdapter((item, item.REQUEST),
                                           name='breadcrumbs_view')
        raw_breadcrumb_titles = breadcrumbs_view.breadcrumbs()

    # Make sure all titles are utf-8
    for elem in raw_breadcrumb_titles:
        title = elem.get('Title')
        if isinstance(title, unicode):
            title = title.encode('utf-8')
        breadcrumb_titles.append(title)

    return breadcrumb_titles


def linked(item, value):
    """Takes an item (object or brain) and returns a HTML snippet that
    contains a link to the item, it's icon and breadcrumbs in the tooltip.
    """

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    # Determine URL method
    url_method = lambda: '#'
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    # Construct CSS class
    css_class = get_css_class(item)

    # Construct breadcrumbs
    breadcrumb_titles = _breadcrumbs_from_item(item)
    link_title = " > ".join(t for t in breadcrumb_titles)

    # Make sure all data used in the HTML snippet is properly escaped
    link_title = cgi.escape(link_title, quote=True)
    value = cgi.escape(value, quote=True)

    link = '<a class="rollover-breadcrumb %s" href="%s" title="%s">%s</a>' % (
        css_class, url_method(), link_title, value)

    wrapper = '<span class="linkWrapper">%s</span>' % link
    return wrapper


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


def overdue_date_helper(item, date):
    """Helper for setting CSS class `overdue` if an item's
    deadline is in the past.

    Partially based on ftw.table.helper.readable_date
    """

    if not date:
        return u''

    strftimestring = '%d.%m.%Y'

    overdue = False
    try:
        formatted_date = date.strftime(strftimestring)
        if dt.fromordinal(date.toordinal()) < dt.today():
            overdue = True
    except ValueError:
        return None

    if overdue and item and item.review_state in [
        'task-state-cancelled',
        'task-state-rejected',
        'task-state-tested-and-closed',
        'forwarding-state-closed']:

        overdue = False

    class_attr = overdue and 'class="overdue"' or ''
    return """<span %s>%s</span>""" % (class_attr, formatted_date)


def queue_view_helper(item, value):
    site = getSite()
    return """<a href='%s/jobs_view?queue=%s'>%s</a>""" % (
        site.absolute_url(), value, value)


def external_edit_link(item, value):
    """Return a link Tag to the checkout_documents view,
    with the external_edit mode selected """
    if item.portal_type != 'opengever.document.document':
        return ''
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
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


def display_client_title_condition():
    """A helper for hiding the client title from a task listing if we
    have a single client setup (it would be the same all the time).
    """
    info = getUtility(IContactInformation)
    if len(info.get_clients()) <= 1:
        # Single client setup - hide the client title column
        return False

    else:
        # Multi client setup - display the client title column
        return True
