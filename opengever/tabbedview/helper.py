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
                                      for k, v in attrs.items()])


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
    img = '<img src="%s/%s"/>' % (item.portal_url(),
                                  item.getIcon.encode('utf-8'))

    breadcrumb_titles = []
    for elem in item.breadcrumb_titles:
        if isinstance(elem.get('Title'), unicode):
            breadcrumb_titles.append(elem.get('Title').encode('utf-8'))
        else:
            breadcrumb_titles.append(elem.get('Title'))
    link = '%s&nbsp;<a class="rollover-breadcrumb" href="%s" title="%s">%s</a>' % (
        img, url_method(),
        " &gt; ".join(t for t in breadcrumb_titles),
        value.encode('utf-8'))
    wrapper = '<span class="linkWrapper">%s</span>' % link
    return wrapper

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

