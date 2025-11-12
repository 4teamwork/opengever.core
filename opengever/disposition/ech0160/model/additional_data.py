from datetime import date
from opengever.disposition import _
from opengever.disposition.ech0160.bindings import arelda
from opengever.propertysheets.utils import get_custom_properties
from zope.globalrequest import getRequest
from zope.i18n import translate


def get_additional_data(obj):
    custom_props = get_custom_properties(obj)
    zusatzdaten = arelda.zusatzDaten()
    for key, value in custom_props.items():
        if value is None:
            continue

        if isinstance(value, list) or isinstance(value, set):
            value = u', '.join(value)

        if isinstance(value, bool):
            if value:
                value = translate(
                    _(u'label_yes', default=u'Yes'), context=getRequest())
            else:
                value = translate(
                    _(u'label_no', default=u'No'), context=getRequest())

        if isinstance(value, int):
            value = str(value)

        if isinstance(value, date):
            value = value.isoformat()

        zusatzdaten.merkmal.append(value)
        zusatzdaten.merkmal[-1].name = key

    if len(zusatzdaten.merkmal):
        return zusatzdaten

    return None
