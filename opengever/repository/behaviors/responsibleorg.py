from opengever.base.model import UNIT_ID_LENGTH
from opengever.repository import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IResponsibleOrgUnit(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=['responsible_org_unit'],
        )

    responsible_org_unit = schema.TextLine(
        title=_(
            u'responsible_org_unit',
            default=u'Responsible organisation unit'),
        description=u'',
        max_length=UNIT_ID_LENGTH,
        required=False,
        )


alsoProvides(IResponsibleOrgUnit, IFormFieldProvider)
