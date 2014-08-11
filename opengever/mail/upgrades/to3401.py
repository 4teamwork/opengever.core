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

        behaviors.extend([
            u'ftw.journal.interfaces.IAnnotationsJournalizable',
            u'opengever.document.behaviors.metadata.IDocumentMetadata',
            u'opengever.document.behaviors.name_from_title.IDocumentNameFromTitle'])

        fti._updateProperty('behaviors', tuple(behaviors))

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize metadata on mail'):
            initialize_metadata(mail, None)
            self.set_receipt_date_equals_creation_date(mail)
            self.set_default_values_for_missing_fields(mail)

    def set_receipt_date_equals_creation_date(self, mail):
        mail_metadata = IDocumentMetadata(mail)
        mail_metadata.receipt_date = mail.created().asdatetime().date()

    def set_default_values_for_missing_fields(self, mail):

        fields = [
            u'keywords',
            u'foreign_reference',
            u'document_type',
            u'digitally_available',
            u'preserved_as_paper',
            u'archival_file',
            u'delivery_date',
            u'thumbnail',
            u'preview',
        ]

        for fieldname in fields:
            field = IDocumentMetadata[fieldname]
            default_adapter = queryMultiAdapter(
                (mail.aq_parent, mail.REQUEST, None, field, None),
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
