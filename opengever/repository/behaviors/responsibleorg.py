from opengever.repository import _
from plone.directives import form
from zope import schema
from zope.interface import Interface, alsoProvides


class IResponsibleOrgUnit(form.Schema):

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=['responsible_org_unit'],
        )

    responsible_org_unit = schema.TextLine(
        title=_(
            u'responsible_org_unit',
            default=u'Responsible organisation unit'),
        description=u'',
        required=False,
        )


alsoProvides(IResponsibleOrgUnit, form.IFormFieldProvider)
