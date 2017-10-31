from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.dossier import _
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface


class IProtectDossierMarker(Interface):
    """Marker interface for the protect dossier behavior"""


class IProtectDossier(model.Schema):

    model.fieldset(
        u'protect',
        label=_(u'fieldset_protect', default=u'Protect'),
        fields=['reading',
                'reading_and_writing'],
        )

    form.widget('reading', KeywordFieldWidget, async=True)
    form.write_permission(reading='opengever.dossier.ProtectDossier')
    reading = schema.List(
        title=_(u'label_reading', default=u'Reading'),
        description=_(
            u'description_reading',
            default=u'Choose users and groups which have only readable access to the dossier'),
        value_type=schema.Choice(source=AllUsersAndGroupsSourceBinder()),
        required=False,
        missing_value=[],
        )

    form.widget('reading_and_writing', KeywordFieldWidget, async=True)
    form.write_permission(reading_and_writing='opengever.dossier.ProtectDossier')
    reading_and_writing = schema.List(
        title=_(u'label_reading_and_writing', default=u'Reading and writing'),
        description=_(
            u'description_reading_and_writing',
            default=u'Choose users and groups which have readable and writing access to the dossier'),
        value_type=schema.Choice(source=AllUsersAndGroupsSourceBinder()),
        required=False,
        missing_value=[],
        )

alsoProvides(IProtectDossier, IFormFieldProvider)
