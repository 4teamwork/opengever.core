from base64 import b64decode
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.models.service import ogds_service
from opengever.sign.sign import Signer
from plone import api
from plone.supermodel.model import Schema
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import os


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentFinalizeTransitionExtender(TransitionExtender):

    def after_transition_hook(self, transition, disable_sync, transition_params):
        """Set finalizer
        """
        self.context.finalizer = api.user.get_current().getId()


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentFinalSigningTransitionExtender(TransitionExtender):

    def after_transition_hook(self, *args, **kwargs):
        """Start signing process
        """
        actor = ogds_service().fetch_user(api.user.get_current().id)
        if not actor or not actor.email:
            raise NoEmailError()

        Signer(self.context).start_signing(editors=[actor.email])


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentDraftSigningTransitionExtender(TransitionExtender):

    def after_transition_hook(self, *args, **kwargs):
        finalize_transition_extender = getMultiAdapter(
            (self.context, self.request),
            ITransitionExtender,
            name="document-transition-finalize")

        finalize_transition_extender.after_transition_hook(*args, **kwargs)

        signing_transition_extender = getMultiAdapter(
            (self.context, self.request),
            ITransitionExtender,
            name="document-transition-final-signing")

        signing_transition_extender.after_transition_hook(*args, **kwargs)


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentSigningFinalTransitionExtender(TransitionExtender):

    def after_transition_hook(self, *args, **kwargs):
        Signer(self.context).abort_signing()


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentSignedDraftTransitionExtender(TransitionExtender):

    def after_transition_hook(self, *args, **kwargs):
        finalized_version_number = self.context.get_current_version_id(
            missing_as_zero=True) - 1

        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.revert_to_version(finalized_version_number)


class ISignSchema(Schema):
    filedata = schema.ASCIILine(
        title=_('label_signed_pdf_filedata',
                default='Base64 encoded signed pdf file data'),
        required=True,
    )


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentSigningSignedTransitionExtender(TransitionExtender):

    schemas = [ISignSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        filedata = b64decode(transition_params.get('filedata'))
        comment = _(u'label_document_signed', default=u'Document signed')
        self.context.update_file(
            data=filedata,
            content_type=u'application/pdf',
            filename=self.get_file_name(),
            create_version=True,
            comment=translate(comment, context=self.request))
        Signer(self.context).finish_signing()

    def get_file_name(self):
        filename, ext = os.path.splitext(self.context.get_filename())
        return u'{}.pdf'.format(filename)


class NoEmailError(Exception):
    """The current user does not have an email defined.
    """
