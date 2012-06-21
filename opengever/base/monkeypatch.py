"""
Filename with umlauts are not supported yet, so we need to patch that.
Therefore we need to patch:
* Products.Five.browser.decode.processInputs
Filenames of FileUpload objects should be converted to unicode as well
* plone.formwidget.namedfile.widget.filename_encoded
Urllib has a problem with filename, which is now unicode and not utf8
any more. So we need to convert it back to utf8 for urllib.
patched for: plone.formwidget.namedfile == 1.0b2

For further details see:
* https://extranet.4teamwork.ch/projects/opengever-kanton-zug/sprint-backlog/111
* http://code.google.com/p/dexterity/issues/detail?id=101
* https://bugs.launchpad.net/zope2/+bug/499696
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import decode
from ZPublisher.HTTPRequest import FileUpload
import logging
import urllib
import z3c.form.interfaces


LOGGER = logging.getLogger('opengever.base')


def processInputs(request, charsets=None):
    if charsets is None:
        envadapter = decode.IUserPreferredCharsets(request)
        charsets = envadapter.getPreferredCharsets() or ['utf-8']

    for name, value in request.form.items():
        if not (decode.isCGI_NAME(name) or name.startswith('HTTP_')):
            if isinstance(value, str):
                request.form[name] = decode._decode(value, charsets)
            elif isinstance(value, list):
                request.form[name] = [decode._decode(val, charsets)
                                       for val in value
                                       if isinstance(val, str)]
            elif isinstance(value, tuple):
                request.form[name] = tuple([decode._decode(val, charsets)
                                             for val in value
                                             if isinstance(val, str)])
            # new part
            elif isinstance(
                value, FileUpload) and isinstance(value.filename, str):
                value.filename = decode._decode(value.filename, charsets)
            # / new part


decode.processInputs = processInputs
LOGGER.info('Monkey patched Products.Five.browser.decode.processInputs')


# --------
class Foo(object):
    @property
    def filename_encoded(self):
        filename = self.filename
        # new part
        if isinstance(filename, unicode):
            filename = filename.encode('utf8')
        # / new part
        if filename is None:
            return None
        else:
            return urllib.quote_plus(filename)

from plone.formwidget.namedfile import widget
setattr(widget.NamedFileWidget,
        'filename_encoded',
        Foo.filename_encoded)
LOGGER.info('Monkey patched plone.formwidget.namedfile.widget.'
            'NameFileWidget.filename_encoded')

# --------

import Products.LDAPUserFolder

Products.LDAPUserFolder.utils.encoding = 'utf-8'
LOGGER.info('Monkey patched Products.LDAPUserFolder.utils.encoding (utf-8)')


# --------

def _fix_terms(self):
    """Fix URLs of the relatedItems terms so virtual hosting still works.
    """
    portal_url_tool = getToolByName(self.context, 'portal_url')
    portal = portal_url_tool.getPortalObject()
    portal_url = portal.absolute_url()

    vhost = portal_url
    vhost = vhost.lstrip('https://')
    vhost = vhost.lstrip('http://')
    vhost_tokens = vhost.split('/')
    vhost_prefix = '/' + '/'.join(vhost_tokens[1:])

    for term in self.terms:
        if term.token.startswith('/%s' % portal.id):
            term.token = term.token.replace('/%s' % portal.id, '')
            term.token = vhost_prefix + term.token


def render(self):
    if self.mode == z3c.form.interfaces.DISPLAY_MODE:
        self._fix_terms()
        return self.display_template(self)
    elif self.mode == z3c.form.interfaces.HIDDEN_MODE:
        return self.hidden_template(self)
    else:
        return self.input_template(self)

import plone.formwidget.contenttree
plone.formwidget.contenttree.widget.ContentTreeBase._fix_terms = _fix_terms
plone.formwidget.contenttree.widget.ContentTreeBase.render = render
LOGGER.info(
    'Monkey patched plone.formwidget.contenttree.widget.ContentTreeBase')

# --------

import webdav.LockItem
 # 24 hours
webdav.LockItem.DEFAULTTIMEOUT = 24 * 60 * 60L
LOGGER.info('Monkey patched webdav.LockItem.DEFAULTTIMEOUT')
