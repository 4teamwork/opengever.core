from plone.autoform.form import AutoExtensibleForm
from plone.api.portal import show_message
from plone.supermodel import model
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFDefault.utils import checkEmailAddress
from z3c.form import button
from z3c.form import form
from zeep.exceptions import Fault as ZeepFault
from zope import schema
from zope.component import getUtility

from opengever.briefbutler.interfaces import IBriefButler
from opengever.briefbutler import _
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.base.utils import get_current_admin_unit


class InvalidEmailAddress(schema.ValidationError):
    __doc__ = _(u'Invalid email address')


def validateaddress(value):
    try:
        checkEmailAddress(value)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(value)
    return True


class ISendFormSchema(model.Schema):

    # the fields of the receiver
    recipient_given_name = schema.TextLine(
        title=_(u'Given Name'),
    )
    recipient_family_name = schema.TextLine(
        title=_(u'Family Name'),
    )
    recipient_street = schema.TextLine(
        title=_(u'Street'),
    )
    recipient_door_number = schema.TextLine(
        required=False,
        title=_(u'Door Number'),
    )
    recipient_postal_code = schema.TextLine(
        title=_(u'Postal Code'),
    )
    recipient_city = schema.TextLine(
        title=_(u'City'),
    )
    recipient_email = schema.TextLine(
        title=_(u'Email'),
        constraint=validateaddress,
    )

    sender_company_name = schema.TextLine(
        title=_(u'Company Name'),
    )
    sender_street = schema.TextLine(
        title=_(u'Street'),
    )
    sender_door_number = schema.TextLine(
        required=False,
        title=_(u'Door Number'),
    )
    sender_postal_code = schema.TextLine(
        title=_(u'Postal Code'),
    )
    sender_city = schema.TextLine(
        title=_(u'City'),
    )

    # group them fields!
    model.fieldset(
        'recipient',
        label=_(u'Recipient Information'),
        fields=['recipient_given_name', 'recipient_family_name',
                'recipient_street', 'recipient_door_number',
                'recipient_postal_code', 'recipient_city', 'recipient_email']
    )
    model.fieldset(
        'sender',
        label=_(u'Sender Information'),
        fields=['sender_company_name', 'sender_street', 'sender_door_number',
                'sender_postal_code', 'sender_city']
    )


class SendForm(AutoExtensibleForm, form.Form):

    schema = ISendFormSchema
    ignoreContext = True
    label = _(u'Send with BriefButler')

    def available(self):
        return bool('yessir')

    @button.buttonAndHandler(_(u'Send'))
    def handle_send(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        else:
            butler = getUtility(IBriefButler)
            try:
                butler.send(self.context, data)
            except ZeepFault as e:
                self.context
                show_message(e.message, self.request, type='error')
                self.request.response.redirect(self.context.absolute_url())
                return

            show_message(_(u'Document submitted to BriefButler'),
                         self.request,
                         type='info')
            self.request.response.redirect(self.context.absolute_url())
            return

        return self.render()

    def render(self):
        if self.context.file.contentType != 'application/pdf':
            show_message(
                _(u'Unsupported content type: '
                  'BriefButler supports only PDF documents'),
                self.request,
                type='error')
            self.request.response.redirect(self.context.absolute_url())
            return
        return super(SendForm, self).render()

    def update(self):
        super(SendForm, self).update()

        if not self.request.form:
            current_user = ogds_service().fetch_current_user()
            if current_user is not None:
                for group in self.groups:
                    # only one of the fields in the fieldset needs to match to be
                    # sure that we're in the right group
                    if 'sender_company_name' in group.widgets:
                        group.widgets['sender_company_name'].value = getattr(
                            get_current_admin_unit(),
                            'title',
                            u''
                        )
                        group.widgets['sender_street'].value = getattr(
                            current_user,
                            'address1',
                            u''
                        )
                        group.widgets['sender_door_number'].value = getattr(
                            current_user,
                            'address2',
                            u''
                        )
                        group.widgets['sender_postal_code'].value = getattr(
                            current_user,
                            'zip_code',
                            u''
                        )
                        group.widgets['sender_city'].value = getattr(
                            current_user,
                            'city',
                            u''
                        )
