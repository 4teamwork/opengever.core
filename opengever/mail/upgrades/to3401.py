from Acquisition import aq_base
from Acquisition import aq_parent
from datetime import datetime
from ftw.mail import utils
from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.mail.mail import get_author_by_email
from plone.dexterity.interfaces import IDexterityFTI
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
import zope.schema


NEW_BEHAVIORS = [
    u'ftw.journal.interfaces.IAnnotationsJournalizable',
    u'opengever.document.behaviors.metadata.IDocumentMetadata',
    u'opengever.document.behaviors.name_from_title.IDocumentNameFromTitle']


class ActivateBehaviors(UpgradeStep):

    def __call__(self):

        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        if 'plone.app.content.interfaces.INameFromTitle' in behaviors:
            behaviors.remove('plone.app.content.interfaces.INameFromTitle')

        for behavior in NEW_BEHAVIORS:
            if not behavior in behaviors:
                behaviors.append(behavior)

        fti._updateProperty('behaviors', tuple(behaviors))

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize metadata on mail',
                                 savepoints=500):
            self.initialize_required_metadata(mail)
            self.set_default_values_for_missing_fields(mail)
            # Indexes and catalog metadata for these objects will be rebuilt in
            # upgrade step opengever.policy.base.upgrades:3400

    def initialize_required_metadata(self, mail):
        mail_metadata = IDocumentMetadata(mail)

        date_time = datetime.fromtimestamp(
            utils.get_date_header(mail.msg, 'Date'))
        mail_metadata.document_date = date_time.date()

        # Receipt date should be None for migrated mails
        mail_metadata.receipt_date = None
        mail_metadata.document_author = get_author_by_email(mail)

    def set_preserved_as_paper(self, mail):
        field = IDocumentMetadata[u'preserved_as_paper']
        default_adapter = queryMultiAdapter(
            (aq_parent(mail), mail.REQUEST, None, field, None),
            IValue, name='default')
        value = default_adapter.get()
        field.set(field.interface(mail), value)

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

            if fieldname == u'preserved_as_paper':
                # preserved_as_paper as acquired as a schema default value
                # - we therefore directly set the value from the default
                # value adapter to avoid picking up the schema default
                self.set_preserved_as_paper(mail)
                continue

            # `digitally_available` is always True for mails
            if fieldname == u'digitally_available':
                field.set(field.interface(mail), True)
                continue

            # Don't overwrite existing values.
            if hasattr(aq_base(mail), fieldname):
                # Existing value - skip unless it's a broken tuple
                if not (isinstance(field, zope.schema._field.Tuple) and
                        getattr(mail, fieldname) is None):
                    continue

            default_adapter = queryMultiAdapter(
                (aq_parent(mail), mail.REQUEST, None, field, None),
                IValue, name='default')

            default = None
            if default_adapter is not None:
                default = default_adapter.get()

            if default is None:
                default = field.default

            if default is None:
                try:
                    default = field.missing_value
                except AttributeError:
                    pass

            # default and missing_value are broken for
            # zope.schema.Tuple - account for that
            if isinstance(field, zope.schema._field.Tuple):
                default = ()

            field.set(field.interface(mail), default)
