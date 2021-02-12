from datetime import datetime
from lxml import etree
from lxml.builder import E
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.document.docprops import DocPropertyCollector
from plone import api
from Products.Five import BrowserView
from zExceptions import NotFound


class DocugateXMLView(BrowserView):

    def __call__(self):
        if not self.is_allowed():
            raise NotFound()

        doc = E(
            "docugate",
            E("docproperties", *self.doc_properties()),
            ResetInterfaceCacheAfterDocCreation="false",
            FreeDocumentSelection="true",
        )
        self.request.response.setHeader("Content-type", "application/xml")
        return etree.tostring(
            doc, pretty_print=True, xml_declaration=True, encoding='utf-8')

    def is_allowed(self):
        if (
            IDocumentFromDocugate.providedBy(self.context)
            and self.context.is_shadow_document()
        ):
            return True
        return False

    def doc_properties(self):
        elements = []
        doc_properties = DocPropertyCollector(self.context).get_properties()
        for key in sorted(doc_properties.keys()):
            value = doc_properties[key]
            if value is None:
                continue
            if isinstance(value, datetime):
                value = api.portal.get_localized_time(value)
            elif isinstance(value, str):
                value = value.decode('utf8')
            elif not isinstance(value, unicode):
                value = unicode(value)
            elements.append(E(key, value))
        return elements
