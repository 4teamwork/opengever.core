# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.testing import IntegrationTestCase
from zope.interface import alsoProvides


class TestDocugateXMLView(IntegrationTestCase):

    features = ("officeconnector-checkout", "docugate")

    @browsing
    def test_xml_view_returns_docugate_xml(self, browser):
        self.login(self.dossier_responsible, browser)
        alsoProvides(self.shadow_document, IDocumentFromDocugate)
        browser.open(self.shadow_document, view='@@docugate-xml')

        expected_xml = """<?xml version='1.0' encoding='utf-8'?>
<docugate FreeDocumentSelection="true" ResetInterfaceCacheAfterDocCreation="false">
  <docproperties>
    <Document.ReferenceNumber>Client1 1.1 / 1 / 41</Document.ReferenceNumber>
    <Document.SequenceNumber>41</Document.SequenceNumber>
    <Dossier.ReferenceNumber>Client1 1.1 / 1</Dossier.ReferenceNumber>
    <Dossier.Title>Verträge mit der kantonalen Finanzverwaltung</Dossier.Title>
    <User.FullName>Ziegler Robert</User.FullName>
    <User.ID>robert.ziegler</User.ID>
    <ogg.document.classification>unprotected</ogg.document.classification>
    <ogg.document.creator.user.email>robert.ziegler@gever.local</ogg.document.creator.user.email>
    <ogg.document.creator.user.firstname>Robert</ogg.document.creator.user.firstname>
    <ogg.document.creator.user.lastname>Ziegler</ogg.document.creator.user.lastname>
    <ogg.document.creator.user.title>Ziegler Robert</ogg.document.creator.user.title>
    <ogg.document.creator.user.userid>robert.ziegler</ogg.document.creator.user.userid>
    <ogg.document.document_date>Aug 31, 2016</ogg.document.document_date>
    <ogg.document.reference_number>Client1 1.1 / 1 / 41</ogg.document.reference_number>
    <ogg.document.sequence_number>41</ogg.document.sequence_number>
    <ogg.document.title>Schättengarten</ogg.document.title>
    <ogg.document.version_number>0</ogg.document.version_number>
    <ogg.dossier.external_reference>qpr-900-9001-÷</ogg.dossier.external_reference>
    <ogg.dossier.reference_number>Client1 1.1 / 1</ogg.dossier.reference_number>
    <ogg.dossier.sequence_number>1</ogg.dossier.sequence_number>
    <ogg.dossier.title>Verträge mit der kantonalen Finanzverwaltung</ogg.dossier.title>
    <ogg.user.email>robert.ziegler@gever.local</ogg.user.email>
    <ogg.user.firstname>Robert</ogg.user.firstname>
    <ogg.user.lastname>Ziegler</ogg.user.lastname>
    <ogg.user.title>Ziegler Robert</ogg.user.title>
    <ogg.user.userid>robert.ziegler</ogg.user.userid>
  </docproperties>
</docugate>
"""
        self.assertEqual(
            browser.contents,
            expected_xml
        )

    @browsing
    def test_xml_view_returns_404_if_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        with browser.expect_http_error(404):
            browser.open(self.document, view="@@docugate-xml")
