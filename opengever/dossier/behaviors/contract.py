from collective.elephantvocabulary import wrap_vocabulary
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.dossier import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


renewal_types = []


class IContract(form.Schema):
    """Behaviour for the contract dossier providing some additional contract
    specific fields.
    """

    form.fieldset(
        u'contract',
        label=_(u'fieldset_contract', u'Contract'),
        fields=[
            u'lifespan',
            u'renewal_type',
            u'extension_deadline',
            u'cancellation_type',
            u'money_type',
            u'cash_periodicity',
            u'amount',
        ],
    )

    lifespan = schema.Int(
        title=_(u'label_lifespan', default=u'Life span'),
        description=_(u'help_lifespan', default=u'Number of months'),
        required=False,
    )

    renewal_type = schema.Choice(
        title=_(u'label_renewal_type', default=u'Renewal type'),
        source=wrap_vocabulary('opengever.dossier.contract_renewal_types'),
        required=False,
    )

    form.widget(extension_deadline=DatePickerFieldWidget)
    extension_deadline = schema.Date(
        title=_(u'label_extension_deadline', default=u'Extension deadline'),
        required=False,
    )

    cancellation_type = schema.Choice(
        title=_(u'label_cancellation_type', default=u'Cancellation type'),
        source=wrap_vocabulary('opengever.dossier.contract_cancellation_types'),
        required=False,
    )

    money_type = schema.TextLine(
        title=_(u'label_money_type', default=u'Money type'),
        required=False,
    )

    cash_periodicity = schema.TextLine(
        title=_(u'label_cash_periodicity', default=u'Cash periodicity'),
        required=False,
    )

    amount = schema.Float(
        title=_(u'label_amount', default=u'Amount'),
        required=False,
    )


alsoProvides(IContract, IFormFieldProvider)
