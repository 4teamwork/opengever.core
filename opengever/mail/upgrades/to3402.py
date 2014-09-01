from Acquisition import aq_base
from Acquisition import aq_parent
from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.classification import IClassification
from plone.dexterity.interfaces import IDexterityFTI
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
import zope.schema


class AddClassifiactionBehavior(UpgradeStep):

    def __call__(self):
        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        behaviors.append(
            'opengever.base.behaviors.classification.IClassification')
        fti._updateProperty('behaviors', tuple(behaviors))

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize IClassification metadata on mail'):
            self.set_default_values(mail)
        # Indexes and catalog metadata for these objects will be rebuilt in
        # upgrade step opengever.policy.base.upgrades:3400

    def set_default_values(self, mail):
        fields = [
            u'classification',
            u'privacy_layer',
            u'public_trial',
            u'public_trial_statement']

        for fieldname in fields:
            field = IClassification[fieldname]

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
