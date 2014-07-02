from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.classification import IClassification
from plone.dexterity.interfaces import IDexterityFTI
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter


class AddClassifiactionBehavior(UpgradeStep):

    def __call__(self):
        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        behaviors.append(
            'opengever.base.behaviors.classification.IClassification')
        fti._updateProperty('behaviors', tuple(behaviors))

        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Initialize metadata on mail'):
            self.set_default_values(mail)

    def set_default_values(self, mail):
        fields = [
            u'classification',
            u'privacy_layer',
            u'public_trial',
            u'public_trial_statement']

        for fieldname in fields:
            field = IClassification[fieldname]
            default_adapter = queryMultiAdapter(
                (mail.aq_parent, mail.REQUEST, None, field, None),
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

            field.set(field.interface(mail), default)
