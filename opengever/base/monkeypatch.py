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

from ZPublisher.HTTPRequest import FileUpload
from Products.Five.browser import decode

def processInputs(request, charsets=None):
    if charsets is None:
        envadapter = decode.IUserPreferredCharsets(request)
        charsets = envadapter.getPreferredCharsets() or ['utf-8']

    for name, value in request.form.items():
        if not (decode.isCGI_NAME(name) or name.startswith('HTTP_')):
            if isinstance(value, str):
                request.form[name] = decode._decode(value, charsets)
            elif isinstance(value, list):
                request.form[name] = [ decode._decode(val, charsets)
                                       for val in value
                                       if isinstance(val, str) ]
            elif isinstance(value, tuple):
                request.form[name] = tuple([ decode._decode(val, charsets)
                                             for val in value
                                             if isinstance(val, str) ])
            # new part
            elif isinstance(value, FileUpload) and isinstance(value.filename, str):
                value.filename = decode._decode(value.filename, charsets)
            # / new part


decode.processInputs = processInputs
print '* [opengever.base] Monkey patched Products.Five.browser.decode.processInputs'



# --------

import urllib

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
print '* [opengever.base] Monkey patched plone.formwidget.namedfile.widget.NameFileWidget.filename_encoded'

# --------

# XXX remove after problem is solved in dexterity
def patched_getCopy(self, container):
    """ _getCopy: patched method removes the __parent__ of the object before copying it.
    This was done due to a bug in dexterity / plone.folder, which results in multiplying
    every object in the site when copy/pasting any object.
    Discussion:
    http://groups.google.com/group/dexterity-development/t/7ca5b06acbc600e7
    """
    # Commit a subtransaction to:
    # 1) Make sure the data about to be exported is current
    # 2) Ensure self._p_jar and container._p_jar are set even if
    # either one is a new object

    # remove parent pointer
    uw_obj = self.aq_self
    parent = None
    if hasattr(uw_obj, '__parent__'):
        parent = self.__parent__
        self.__parent__ = None

    transaction.savepoint(optimistic=True)

    if self._p_jar is None:
        raise CopyError, (
            'Object "%s" needs to be in the database to be copied' %
            `self`)
    if container._p_jar is None:
        raise CopyError, (
            'Container "%s" needs to be in the database' %
            `container`)

    # Ask an object for a new copy of itself.
    f=tempfile.TemporaryFile()
    self._p_jar.exportFile(self._p_oid,f)
    f.seek(0)
    ob=container._p_jar.importFile(f)
    f.close()

    # # restore parentpointer
    if parent:
        self.__parent__ = parent

    return ob

