from five import grok
from opengever.inbox.forwarding import IForwarding
from opengever.task import _
from plone.directives import form
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema


class IForwardingCloseSchema(form.Schema):

    text = schema.Text(
        title=_('label_response', default="Response"),
        description=_('help_response', default=""),
        required=False,
        )


class ForwardingCloseForm(Form):

    fields = Fields(IForwardingCloseSchema)
    label = _(u'title_close_forwarding', u'Close Forwarding')
    ignoreContext = True

    @buttonAndHandler(_(u'button_close', default=u'Close'))
    def handle_close(self, action):
        data, errors = self.extractData()
        if not errors:
            store_view = self.context.restrictedTraverse(
                'store_forwarding_in_yearfolder')
            store_view.store_to_yearfolder(text=data.get('text'))
            return self.request.RESPONSE.redirect('.')

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ForwardingCloseView(layout.FormWrapper, grok.View):
    grok.context(IForwarding)
    grok.name('forwarding_close')
    grok.require('zope2.View')

    form = ForwardingCloseForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__
