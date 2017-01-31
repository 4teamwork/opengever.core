from opengever.base import monkey  # noqa
from plone.i18n.locales import languages
from zope.i18nmessageid import MessageFactory
import csv


_ = MessageFactory('opengever.base')

VERSION = 'GEVER Version %(version)s'


class OpenGeverCSVDialect(csv.excel):
    """A CSV dialect based on the standard Excel dialect but with support for
    escaped characters (double quotes in particular).
    """
    escapechar = '\\'


csv.register_dialect(u'OpenGeverCSV', OpenGeverCSVDialect)


# configure visible language codes. Unfortunately this cannot be done in a .po
# file.
languages._combinedlanguagelist['de-ch']['native'] = u'DE'
languages._combinedlanguagelist['fr-ch']['native'] = u'FR'

def initialize(context):
    from opengever.base.indexes import UserTurboIndex
    from opengever.base.indexes import manage_addUserTurboIndex
    from opengever.base.indexes import manage_addUserTurboIndexForm
    context.registerClass(UserTurboIndex,
                          permission='Add Pluggable Index',
                          constructors=(manage_addUserTurboIndexForm,
                                        manage_addUserTurboIndex),
                          visibility=None)
