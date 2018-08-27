from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.repository import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides


class IResponsibleOrgUnit(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=['responsible_org_unit'],
        )

    form.widget('responsible_org_unit', KeywordFieldWidget, new_terms_as_unicode=True)
    responsible_org_unit = ChoicePlus(
        title=_(u'responsible_org_unit', default=u'Responsible organisation unit'),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=False,
        )


alsoProvides(IResponsibleOrgUnit, IFormFieldProvider)
