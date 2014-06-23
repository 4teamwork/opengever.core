from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.mail.mail import initialize_metadata
from plone.dexterity.interfaces import IDexterityFTI
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter


class ActivateBehaviors(UpgradeStep):

    def __call__(self):

        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        if 'plone.app.content.interfaces.INameFromTitle' in behaviors:
            behaviors.remove('plone.app.content.interfaces.INameFromTitle')
        behaviors.append(
            u'ftw.journal.interfaces.IAnnotationsJournalizable')
        behaviors.append(
            u'opengever.document.behaviors.metadata.IDocumentMetadata')

        fti._updateProperty('behaviors', tuple(behaviors))

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize metadata on mail'):
            initialize_metadata(mail, None)
            self.set_receipt_date_equals_creation_date(mail)
            self.update_missing_field_values(mail)

    def set_receipt_date_equals_creation_date(self, mail):
        mail_metadata = IDocumentMetadata(mail)
        mail_metadata.receipt_date = mail.created().asdatetime()

    def update_missing_field_values(self, mail):
        missing_fields = ['keywords', 'foreign_reference', 'delivery_date',
                          'document_type', 'digitally_available',
                          'archival_file', 'thumbnail', 'preview']

        for fieldname in missing_fields:
            field = IDocumentMetadata[fieldname]
            default_adapter = queryMultiAdapter(
                (mail, mail.REQUEST, None, field, None),
                IValue, name='default')

            default = None
            if default_adapter is not None:
                default = default_adapter.get()

            if default is None:
                try:
                    default = field.missing_value
                except AttributeError:
                    pass
            field.set(field.interface(mail), default)
