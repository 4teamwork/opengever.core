from opengever.base.json_response import JSONResponse
from opengever.base.model import create_session
from opengever.base.utils import to_safe_html
from opengever.contact import _
from opengever.contact.models.mailaddress import MailAddress
from plone import api
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMailAddressesActions(Interface):

    def list():
        """Returns json list of all mailaddresses for the current context (contact).
        'plone/contact-3/mails/list'
        """

    def update():
        """Updates the mailaddress attributes, with the one given by
        the request parameter.
        The view expect that its called by traversing over the mailaddress:
        `plone/contact-3/mails/14/update` for example.
        """

    def delete():
        """Remove the given mailaddress.
        The view expect that its called by traversing over the mailaddress:
        `plone/contact-3/mails/14/delete` for example.
        """

    def add():
        """Add a new mail to the database
        'plone/contact-3/mails/add'
        """


class MailAddressesView(BrowserView):

    implements(IBrowserView, IPublishTraverse, IMailAddressesActions)

    def publishTraverse(self, request, name):
        if name in IMailAddressesActions.names():
            return getattr(self, name)

        # we only support exactly one id
        if self.mailaddress_id:
            raise NotFound

        try:
            self.mailaddress_id = int(name)
        except ValueError:
            raise NotFound

        self.mailaddress = MailAddress.query.get(self.mailaddress_id)

        if not self.mailaddress:
            raise NotFound

        if self.mailaddress.contact is not self.contact:
            # Prevent from cross injections
            raise NotFound

        return self

    def __init__(self, context, request):
        super(MailAddressesView, self).__init__(context, request)
        self.contact = self.context.model
        self.mailaddress_id = None
        self.mailaddress = None
        self.session = create_session()

    def add(self):
        label = to_safe_html(self.request.get('label'))
        mailaddress = to_safe_html(self.request.get('mailaddress'))

        error_msg = self._validate(label, mailaddress)

        if error_msg:
            return JSONResponse(self.request).error(error_msg).dump()

        mail_object = MailAddress(
            label=label,
            address=mailaddress,
            contact_id=self.context.model.person_id)

        self.session.add(mail_object)

        msg = _(
            u'info_mailaddress_created',
            u'The email address was created successfully')

        return JSONResponse(self.request).info(msg).proceed().dump()

    def list(self):
        return JSONResponse(self.request).data(
            mailaddresses=self._get_mail_addresses()).dump()

    def update(self):
        label = to_safe_html(self.request.get('label', self.mailaddress.label))
        mailaddress = to_safe_html(self.request.get('mailaddress', self.mailaddress.address))

        error_msg = self._validate(label, mailaddress)

        if error_msg:
            return JSONResponse(self.request).error(error_msg).dump()

        self.mailaddress.update(label=label, address=mailaddress)

        return JSONResponse(self.request).info(
            _('email_address_updated',
              default=u"Email address updated.")).proceed().dump()

    def delete(self):
        self.mailaddress.delete()

        return JSONResponse(self.request).info(
            _(u'mail_address_deleted',
              default=u'Mailaddress successfully deleted')).dump()

    def _get_mail_addresses(self):
        """Returns a serialized email-address-list.
        """
        return [address.serialize() for address in self.contact.mail_addresses]

    def _validate(self, label, mailaddress):
        """Validates the given attributes.

        Returns None if the validation passed.
        Returns the errormessage if the validation failed.
        """
        plone_utils = api.portal.get_tool('plone_utils')

        if not label and not mailaddress:
            return _(
                u'error_no_label_and_email',
                u'Please specify a label and an email address.'
                )

        elif not label:
            return _(
                u'error_no_label', u'Please specify a label for your email address')

        elif not mailaddress:
            return _(
                u'error_no_email', u'Please specify an email address')

        elif not plone_utils.validateSingleEmailAddress(mailaddress):
            return _(
                u'error_invalid_email', u'Please specify a valid email address')
