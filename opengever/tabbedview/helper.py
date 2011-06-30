from datetime import date as dt
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview import _
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import ram
from Products.CMFCore.interfaces._tools import IMemberData
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from zope.app.component.hooks import getSite
from zope.component import getUtility
import ftw.table
from ftw.mail.utils import get_header


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
    if info.is_user(author) or info.is_contact(author) or info.is_inbox(author):
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
    if not isinstance(author, unicode):
        author = author.decode('utf-8')
    if IPropertiedUser.providedBy(author) or IMemberData.providedBy(author):
        author = author.getId()
    info = getUtility(IContactInformation)
    if info.is_user(author) or info.is_contact(author) or info.is_inbox(author):
        return info.render_link(author)
    else:
        return author


def linked(item, value):
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url

    normalize = getUtility(IIDNormalizer).normalize

    if not item.portal_type == 'opengever.document.document':
        css_class = "contenttype-%s" % normalize(item.portal_type)
    else:
        # It's a document, we therefore want to display an icon
        # for the mime type of the contained file
        icon = getattr(item, 'getIcon', '')
        if not icon == '':
            # Strip '.gif' from end of icon name and remove leading 'icon_'
            filetype = icon[:icon.rfind('.')].replace('icon_', '')
            css_class = 'icon-%s' % normalize(filetype)
        else:
            # Fallback for unknown file type
            css_class = "contenttype-%s" % normalize(item.portal_type)

    breadcrumb_titles = []
    for elem in item.breadcrumb_titles:
        if isinstance(elem.get('Title'), unicode):
            breadcrumb_titles.append(elem.get('Title').encode('utf-8'))
        else:
            breadcrumb_titles.append(elem.get('Title'))

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    link = '<a class="rollover-breadcrumb %s" href="%s" title="%s">%s</a>' % (
        css_class, url_method(),
        " &gt; ".join(t for t in breadcrumb_titles),
        value)

    wrapper = '<span class="linkWrapper">%s</span>' % link
    return wrapper


def readable_date(item, date):
    if getattr(item, 'portal_type', None) == 'ftw.mail.mail':
        # Conditional import to avoid dependency on ftw.mail
        from ftw.mail.utils import get_header
        from DateTime import DateTime
        if getattr(item, 'msg', ''):
            # Object
            datestr = get_header(item.msg, 'Date')
            # Thu, 28 Apr 2011 11:38:38 +0200
            date = DateTime(datestr).asdatetime()
        else:
            # Brain
            date = item.document_date.asdatetime()

    if not date:
        return u''
    strftimestring = '%d.%m.%Y'
    if date == None:
        return None
    try:
        return date.strftime(strftimestring)
    except ValueError:
        return None

def readable_date_set_invisibles(item, date):
    if not date or str(date) == '1970/01/01' \
            or str(date) == '1970-01-01 00:00:00':
        return u''
    strftimestring = '%d.%m.%Y'
    if date == None:
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

    return value and _(u'label_yes', default='Yes') or \
                     _(u'label_no', default='No')


def workflow_state(item, value):
    """Helper which translates the workflow_state in plone domain
    and adds a CSS class to indicate the worflow state.
    """
    i18n_translate = getSite().translate
    translate = ftw.table.helper.translated_string('plone')
    translated_value = translate(item, value)
    normalize = getUtility(IIDNormalizer).normalize
    state = normalize(item.review_state)
    return """<span class="wf-%s">%s</span>""" % (state, i18n_translate(translated_value))


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

    if overdue and item and item.review_state in ['task-state-cancelled',
                                                  'task-state-rejected',
                                                  'task-state-tested-and-closed',
                                                  'forwarding-state-closed']:
        overdue = False

    class_attr = overdue and 'class="overdue"' or ''
    return """<span %s>%s</span>""" % (class_attr, formatted_date)


def queue_view_helper(item, value):
    site = getSite()
    return """<a href='%s/jobs_view?queue=%s'>%s</a>""" %(site.absolute_url(),value,value)


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
        getSite().translate('checkout_and_edit',domain="opengever.tabbedview"),
        url)
