from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.inbox import _
from plone.directives import form
from zope import schema


class IInbox(form.Schema, ITabbedviewUploadable):
    """ Inbox for OpenGever
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[u'inbox_group', ],
        )

    inbox_group = schema.TextLine(
         title=_(u'label_inbox_group', default=u'Inbox Group'),
         description=_(u'help_inbox_group', default=u''),
         required=False,
         )
