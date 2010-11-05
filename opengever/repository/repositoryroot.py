from plone.directives import form
from zope import schema
from opengever.repository import _

class IRepositoryRoot(form.Schema):
    """ Repository root marker / schema interface
    """
      
    valid_from = schema.Date(
        title = _(u'label_valid_from', default=u'Valid from'),
        description = _(u'help_valid_from', default=u''),
        required = False,
        )

    valid_until = schema.Date(
        title = _(u'label_valid_until', default=u'Valid until'),
        description = _(u'help_valid_until', default=u''),
        required = False,
        )
    
    version = schema.TextLine(
        title = _(u'label_version', default=u'Version'),
        description = _(u'help_version', default=''),
        required = False,
        )