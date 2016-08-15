from opengever.base.model import create_session
from opengever.base.response import JSONResponse
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
import json
import transaction


class IMailAddressesActions(Interface):

    def list():
        """Returns json list of all mailaddresses for the current context (contact).
        'plone/person-3/mails/list'
        """

    def update():
        """Updates the mailaddress attributes, with the one given by
        the request parameter.
        The view expect that its called by traversing over the mailaddress:
        `plone/person-3/mails/14/update` for example.
        """

    def delete():
        """Remove the given mailaddress.
        The view expect that its called by traversing over the mailaddress:
        `plone/person-3/mails/14/delete` for example.
        """

    def add():
        """Add a new mail to the database
        'plone/person-3/mails/add'
        """

    def set_all():
        """Update add or delete a list of items.
        'plone/person-3/mails/set_all'
        """

    def validate():
        """Update add or delete a list of items.
        'plone/person-3/mails/validate'
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
        response = self._add(
            {'label': to_safe_html(self.request.get('label')),
             'mailaddress': to_safe_html(self.request.get('mailaddress'))})
        return response.dump()

    def _add(self, values):
        label = to_safe_html(values.get('label'))
        mailaddress = to_safe_html(values.get('mailaddress'))

        error_msg = self._validate(label, mailaddress)

        if error_msg:
            return JSONResponse(self.request).error(error_msg)

        mail_object = MailAddress(
            label=label,
            address=mailaddress,
            contact_id=self.context.model.person_id)

        self.session.add(mail_object)

        msg = _(
            u'info_mailaddress_created',
            u'The email address was created successfully')
        return JSONResponse(self.request).info(msg).proceed()

    def list(self):
        return JSONResponse(self.request).data(
            mailaddresses=self._get_mail_addresses()).dump()

    def update(self):
        response = self._update({
            'label': self.request.get('label', self.mailaddress.label),
            'mailaddress': self.request.get('mailaddress', self.mailaddress.address),
        })

        return response.dump()

    def _update(self, values):
        label = to_safe_html(values.get('label'))
        mailaddress = to_safe_html(values.get('mailaddress'))

        error_msg = self._validate(label, mailaddress)

        if error_msg:
            return JSONResponse(self.request).error(error_msg)

        self.mailaddress.update(label=label, address=mailaddress)

        return JSONResponse(self.request).info(
            _('email_address_updated',
              default=u"Email address updated.")).proceed()

    def delete(self):
        self.mailaddress.delete()

        return JSONResponse(self.request).info(
            _(u'mail_address_deleted',
              default=u'Mailaddress successfully deleted')).dump()

    def set_all(self):
        data = json.loads(self.request.get('objects'))
        responses = []
        to_remove = [mail.mailaddress_id for mail in self.contact.mail_addresses]

        for item in data:
            self.mailaddress_id = item.get('id')

            if not item.get('id'):
                responses.append(self._add(item.get('values')))

            else:
                self.mail_address = MailAddress.query.get(self.mailaddress_id)
                responses.append(self._update(item.get('values')))
                to_remove.pop(self.mailaddress_id)

        for mailadddress_id in to_remove:
            MailAddress.query.get(self.mailaddress_id).delete()

        if not all([response.is_proceed() for response in responses]):
            transaction.abort()
            return JSONResponse(self.request).remain().error(
                _('msg_not_saved', default=u'Save failed.')).dump()

        return JSONResponse(self.request).info(
            _('msg_save_successfull', default=u'Save successfuly.')).dump()

    def _get_mail_addresses(self):
        """Returns a serialized email-address-list.
        """
        return [address.serialize() for address in self.contact.mail_addresses]

    def validate(self):
        error_msg = self._validate(self.request.get('label'),
                                   self.request.get('address'))
        if error_msg:
            return JSONResponse(self.request).remain().error(error_msg).dump()

        return JSONResponse(self.request).proceed().dump()


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
