# ./bindings/ablieferung.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2016-04-16 12:49:30.774696 by PyXB version 1.2.5-DEV using Python 2.7.11.final.0
# Namespace AbsentNamespace0
# flake8: noqa

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:e548cfc5-03c0-11e6-820c-c42c03358f75')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.5-DEV'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.CreateAbsentNamespace()
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: ablieferungstyp
class ablieferungstyp (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """Angabe darüber, aus welcher Umgebung die Ablieferung stammt.Indication of the environment from which the submission comes.Indication de l'environnement duquel provient le versement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ablieferungstyp')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 17, 2)
    _Documentation = "Angabe dar\xfcber, aus welcher Umgebung die Ablieferung stammt.Indication of the environment from which the submission comes.Indication de l'environnement duquel provient le versement."
ablieferungstyp._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ablieferungstyp, enum_prefix=None)
ablieferungstyp.GEVER = ablieferungstyp._CF_enumeration.addEnumeration(unicode_value='GEVER', tag='GEVER')
ablieferungstyp.FILES = ablieferungstyp._CF_enumeration.addEnumeration(unicode_value='FILES', tag='FILES')
ablieferungstyp._InitializeFacetMap(ablieferungstyp._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ablieferungstyp', ablieferungstyp)
_module_typeBindings.ablieferungstyp = ablieferungstyp

# Atomic simple type: ca
class ca (pyxb.binding.datatypes.boolean):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ca')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 21, 2)
    _Documentation = ''
ca._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ca', ca)
_module_typeBindings.ca = ca

# Atomic simple type: keineAngabe
class keineAngabe (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'keineAngabe')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 28, 2)
    _Documentation = ''
keineAngabe._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=keineAngabe, enum_prefix=None)
keineAngabe.keine_Angabe = keineAngabe._CF_enumeration.addEnumeration(unicode_value='keine Angabe', tag='keine_Angabe')
keineAngabe._InitializeFacetMap(keineAngabe._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'keineAngabe', keineAngabe)
_module_typeBindings.keineAngabe = keineAngabe

# Union simple type: zeitpunkt
# superclasses pyxb.binding.datatypes.anySimpleType
class zeitpunkt (pyxb.binding.basis.STD_union):

    """Simple type that is a union of pyxb.binding.datatypes.date, pyxb.binding.datatypes.dateTime."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'zeitpunkt')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 63, 2)
    _Documentation = None

    _MemberTypes = ( pyxb.binding.datatypes.date, pyxb.binding.datatypes.dateTime, )
zeitpunkt._CF_pattern = pyxb.binding.facets.CF_pattern()
zeitpunkt._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=zeitpunkt)
zeitpunkt._InitializeFacetMap(zeitpunkt._CF_pattern,
   zeitpunkt._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'zeitpunkt', zeitpunkt)
_module_typeBindings.zeitpunkt = zeitpunkt

# Union simple type: datumTypB
# superclasses pyxb.binding.datatypes.anySimpleType
class datumTypB (pyxb.binding.basis.STD_union):

    """Zeitpunkte: the following values are possible by date type 3 regular expression (technische Anwendung)
        Date Data Type (xs:date)
        The date is specified in the following form "YYYY-MM-DD" where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        Hinweis: Alle Komponenten werden benötigt!

        DateTime Data Type (xs:dateTime)
        The dateTime data type is used to specify a date and a time.
        The dateTime is specified in the following form "YYYY-MM-DDThh:mm:ss" where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        * T indicates the start of the required time section
        * hh indicates the hour
        * mm indicates the minute
        * ss indicates the second
        Hinweis: Alle Komponenten werden benötigt!
      "Time points: the following values are possible by date type 3 regular expression (technical application)
        Date Data Type (xs:date)
        The date is specified in the following form ''YYYY-MM-DD'' where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        Note: All components are required!

        DateTime Data Type (xs:dateTime)
        The dateTime data type is used to specify a date and a time.
        The dateTime is specified in the following form ''YYYY-MM-DDThh:mm:ss'' where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        * T indicates the start of the required time section
        * hh indicates the hour
        * mm indicates the minute
        * ss indicates the second
        Note: All components are required!"Moments: the following values are possible by date type 3 regular expression (application technique)
        Date Data Type (xs:date)
        The date is specified in the following form "YYYY-MM-DD" where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        Remarque : Tous les composants sont n�cessaires!

        DateTime Data Type (xs:dateTime)
        The dateTime data type is used to specify a date and a time.
        The dateTime is specified in the following form "YYYY-MM-DDThh:mm:ss" where:
        * YYYY indicates the year
        * MM indicates the month
        * DD indicates the day
        * T indicates the start of the required time section
        * hh indicates the hour
        * mm indicates the minute
        * ss indicates the second
        Remarque : Tous les composants sont nécessaires!"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'datumTypB')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 74, 2)
    _Documentation = 'Zeitpunkte: the following values are possible by date type 3 regular expression (technische Anwendung)\n        Date Data Type (xs:date)\n        The date is specified in the following form "YYYY-MM-DD" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        Hinweis: Alle Komponenten werden ben\xf6tigt!\n        \n        DateTime Data Type (xs:dateTime)\n        The dateTime data type is used to specify a date and a time.\n        The dateTime is specified in the following form "YYYY-MM-DDThh:mm:ss" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        * T indicates the start of the required time section\n        * hh indicates the hour\n        * mm indicates the minute\n        * ss indicates the second\n        Hinweis: Alle Komponenten werden ben\xf6tigt!\n      "Time points: the following values are possible by date type 3 regular expression (technical application)\n        Date Data Type (xs:date)\n        The date is specified in the following form ""YYYY-MM-DD"" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        Note: All components are required!\n        \n        DateTime Data Type (xs:dateTime)\n        The dateTime data type is used to specify a date and a time.\n        The dateTime is specified in the following form ""YYYY-MM-DDThh:mm:ss"" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        * T indicates the start of the required time section\n        * hh indicates the hour\n        * mm indicates the minute\n        * ss indicates the second\n        Note: All components are required!"Moments: the following values are possible by date type 3 regular expression (application technique)\n        Date Data Type (xs:date)\n        The date is specified in the following form "YYYY-MM-DD" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        Remarque : Tous les composants sont n\ufffdcessaires!\n        \n        DateTime Data Type (xs:dateTime)\n        The dateTime data type is used to specify a date and a time.\n        The dateTime is specified in the following form "YYYY-MM-DDThh:mm:ss" where:\n        * YYYY indicates the year\n        * MM indicates the month\n        * DD indicates the day\n        * T indicates the start of the required time section\n        * hh indicates the hour\n        * mm indicates the minute\n        * ss indicates the second\n        Remarque : Tous les composants sont n\xe9cessaires!'

    _MemberTypes = ( pyxb.binding.datatypes.date, pyxb.binding.datatypes.dateTime, )
datumTypB._CF_pattern = pyxb.binding.facets.CF_pattern()
datumTypB._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=datumTypB)
datumTypB._InitializeFacetMap(datumTypB._CF_pattern,
   datumTypB._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'datumTypB', datumTypB)
_module_typeBindings.datumTypB = datumTypB

# Atomic simple type: text1
class text1 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text1')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 169, 2)
    _Documentation = None
text1._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(100))
text1._InitializeFacetMap(text1._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text1', text1)
_module_typeBindings.text1 = text1

# Atomic simple type: text2
class text2 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text2')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 175, 2)
    _Documentation = None
text2._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(200))
text2._InitializeFacetMap(text2._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text2', text2)
_module_typeBindings.text2 = text2

# Atomic simple type: text3
class text3 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text3')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 181, 2)
    _Documentation = None
text3._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(1000))
text3._InitializeFacetMap(text3._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text3', text3)
_module_typeBindings.text3 = text3

# Atomic simple type: text4
class text4 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text4')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 187, 2)
    _Documentation = None
text4._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'text4', text4)
_module_typeBindings.text4 = text4

# Atomic simple type: ablieferungsnummer
class ablieferungsnummer (text1):

    """Die Ablieferungsnummer dient zur Identifizierung der Ablieferung im Archiv. Sie besteht in der Regel aus dem Ablieferungsjahr und einer Laufnummer innerhalb dieses Jahres. Die Ablieferungsnummer kann auch Buchstaben enthalten.The submission number serves to identify the submission. It consists of the submission year and a consecutive number within that year.Le numéro de versement sert à l'identification du versement aux archives. Il est généralement constitué de l'année du versement et d'un numéro courant de cette année. Le numéro de versement peut aussi contenir des lettres."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ablieferungsnummer')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 7, 2)
    _Documentation = "Die Ablieferungsnummer dient zur Identifizierung der Ablieferung im Archiv. Sie besteht in der Regel aus dem Ablieferungsjahr und einer Laufnummer innerhalb dieses Jahres. Die Ablieferungsnummer kann auch Buchstaben enthalten.The submission number serves to identify the submission. It consists of the submission year and a consecutive number within that year.Le num\xe9ro de versement sert \xe0 l'identification du versement aux archives. Il est g\xe9n\xe9ralement constitu\xe9 de l'ann\xe9e du versement et d'un num\xe9ro courant de cette ann\xe9e. Le num\xe9ro de versement peut aussi contenir des lettres."
ablieferungsnummer._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ablieferungsnummer', ablieferungsnummer)
_module_typeBindings.ablieferungsnummer = ablieferungsnummer

# Atomic simple type: angebotsnummer
class angebotsnummer (text1):

    """Die vom Archiv vergebene Nummer des Angebots, auf welches sich die Ablieferung stützt.The number, allocated by the archive, of the offering on which the submission is based.Le numéro de l'offre qui est donné par les archives et sur lequel se base le versement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'angebotsnummer')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 30, 2)
    _Documentation = "Die vom Archiv vergebene Nummer des Angebots, auf welches sich die Ablieferung st\xfctzt.The number, allocated by the archive, of the offering on which the submission is based.Le num\xe9ro de l'offre qui est donn\xe9 par les archives et sur lequel se base le versement."
angebotsnummer._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'angebotsnummer', angebotsnummer)
_module_typeBindings.angebotsnummer = angebotsnummer

# Atomic simple type: ablieferndeStelle
class ablieferndeStelle (text2):

    """Organisationseinheit, welche die abzuliefernden Unterlagen aufbereitet (der Name wird ausgeschrieben, keine Abkürzung), und Name der Person, die für die Ablieferung zuständig ist.Organisational unit that prepares the documents to be submitted (name written out in full, no abbreviations) and name of the person responsible for the submission.Unité organisationnelle qui prépare les documents à verser (le nom est écrit en toutes lettres, sans abréviation) et nom de la personne qui est responsable du versement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ablieferndeStelle')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 40, 2)
    _Documentation = 'Organisationseinheit, welche die abzuliefernden Unterlagen aufbereitet (der Name wird ausgeschrieben, keine Abk\xfcrzung), und Name der Person, die f\xfcr die Ablieferung zust\xe4ndig ist.Organisational unit that prepares the documents to be submitted (name written out in full, no abbreviations) and name of the person responsible for the submission.Unit\xe9 organisationnelle qui pr\xe9pare les documents \xe0 verser (le nom est \xe9crit en toutes lettres, sans abr\xe9viation) et nom de la personne qui est responsable du versement.'
ablieferndeStelle._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ablieferndeStelle', ablieferndeStelle)
_module_typeBindings.ablieferndeStelle = ablieferndeStelle

# Atomic simple type: referenzBewertungsentscheid
class referenzBewertungsentscheid (text1):

    """Aktenzeichen Bewertungsentscheid(e) Archiv, welches die Ablieferung betreffen.File reference of the appraisal decision(s) relating to the submission.Référence décision(s) d'évaluation archives qui concernent le versement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'referenzBewertungsentscheid')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 50, 2)
    _Documentation = "Aktenzeichen Bewertungsentscheid(e) Archiv, welches die Ablieferung betreffen.File reference of the appraisal decision(s) relating to the submission.R\xe9f\xe9rence d\xe9cision(s) d'\xe9valuation archives qui concernent le versement."
referenzBewertungsentscheid._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'referenzBewertungsentscheid', referenzBewertungsentscheid)
_module_typeBindings.referenzBewertungsentscheid = referenzBewertungsentscheid

# Atomic simple type: referenzSchutzfristenFormular
class referenzSchutzfristenFormular (text1):

    """Aktenzeichen des Formulars „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“, in dem die für die Ablieferung vereinbarten Schutzfristen festgehalten sind.File reference of the "Notification of documents subject to a special closure period and publicly accessible documents" form in which the closure periods agreed for the submission are set down.Référence du formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public", dans lequel sont fixés les délais de protection convenus pour le versement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'referenzSchutzfristenFormular')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 60, 2)
    _Documentation = 'Aktenzeichen des Formulars \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c, in dem die f\xfcr die Ablieferung vereinbarten Schutzfristen festgehalten sind.File reference of the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form in which the closure periods agreed for the submission are set down.R\xe9f\xe9rence du formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public", dans lequel sont fix\xe9s les d\xe9lais de protection convenus pour le versement.'
referenzSchutzfristenFormular._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'referenzSchutzfristenFormular', referenzSchutzfristenFormular)
_module_typeBindings.referenzSchutzfristenFormular = referenzSchutzfristenFormular

# Atomic simple type: schutzfristenkategorieAblieferung
class schutzfristenkategorieAblieferung (text1):

    """Artikel des Gesetztes, der die Schutzfrist festhält, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Article of the law stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristenkategorieAblieferung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 70, 2)
    _Documentation = 'Artikel des Gesetztes, der die Schutzfrist festh\xe4lt, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Article of the law stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristenkategorieAblieferung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'schutzfristenkategorieAblieferung', schutzfristenkategorieAblieferung)
_module_typeBindings.schutzfristenkategorieAblieferung = schutzfristenkategorieAblieferung

# Atomic simple type: schutzfristAblieferung
class schutzfristAblieferung (text1):

    """Dauer der Schutzfrist in Jahren, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Durée en années du délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristAblieferung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 80, 2)
    _Documentation = 'Dauer der Schutzfrist in Jahren, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Dur\xe9e en ann\xe9es du d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristAblieferung._CF_pattern = pyxb.binding.facets.CF_pattern()
schutzfristAblieferung._CF_pattern.addPattern(pattern='[0-9]*')
schutzfristAblieferung._InitializeFacetMap(schutzfristAblieferung._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'schutzfristAblieferung', schutzfristAblieferung)
_module_typeBindings.schutzfristAblieferung = schutzfristAblieferung

# Atomic simple type: ablieferungsteile
class ablieferungsteile (text3):

    """Angabe über den gesamten Inhalt der Ablieferung (sowohl der digitalen als auch der nicht digitalen Teile).Indication of the full content of the submission (both digital and non-digital components).Informations sur le contenu entier du versement (non seulement la partie numérique, mais aussi la partie non numérique)."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ablieferungsteile')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 92, 2)
    _Documentation = 'Angabe \xfcber den gesamten Inhalt der Ablieferung (sowohl der digitalen als auch der nicht digitalen Teile).Indication of the full content of the submission (both digital and non-digital components).Informations sur le contenu entier du versement (non seulement la partie num\xe9rique, mais aussi la partie non num\xe9rique).'
ablieferungsteile._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ablieferungsteile', ablieferungsteile)
_module_typeBindings.ablieferungsteile = ablieferungsteile

# Atomic simple type: bemerkungAblieferung
class bemerkungAblieferung (text4):

    """Zusätzliche Informationen, welche die Ablieferung und ihre Entstehung betreffen. Wenn die Unterlagen in der Ablieferung aus einer periodisierten Registratur stammen, kann hier die Registraturperiode angegeben werden.Additional information relating to the submission and its creation. If the documents in the submission come from a periodised registry, the registry period can be indicated here.Informations complémentaires qui concernent le versement et sa création . Si les documents du versement datent d'une période donnée, la date d'enregistrement peut être indiquée ici."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bemerkungAblieferung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ablieferung.xsd', 102, 2)
    _Documentation = "Zus\xe4tzliche Informationen, welche die Ablieferung und ihre Entstehung betreffen. Wenn die Unterlagen in der Ablieferung aus einer periodisierten Registratur stammen, kann hier die Registraturperiode angegeben werden.Additional information relating to the submission and its creation. If the documents in the submission come from a periodised registry, the registry period can be indicated here.Informations compl\xe9mentaires qui concernent le versement et sa cr\xe9ation . Si les documents du versement datent d'une p\xe9riode donn\xe9e, la date d'enregistrement peut \xeatre indiqu\xe9e ici."
bemerkungAblieferung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bemerkungAblieferung', bemerkungAblieferung)
_module_typeBindings.bemerkungAblieferung = bemerkungAblieferung

# Union simple type: datumTypA
# superclasses pyxb.binding.datatypes.anySimpleType
class datumTypA (pyxb.binding.basis.STD_union):

    """Zeitpunkte: the following values are possible by date type 1 regular expression (historische Anwendung)
        31.01.2004
        ca.31.01.2004
        2004
        ca.2004
        keineAngabe
      "Time points: the following values are possible by date type 1 regular expression (legacy application)
        31.01.2004
        approx.31.01.2004
        2004
        approx.2004
        vMoments: the following values are possible by date type 1 regular expression (application historique)
        31.01.2004
        ca.31.01.2004
        2004
        ca.2004
        keineAngabe"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'datumTypA')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 37, 2)
    _Documentation = 'Zeitpunkte: the following values are possible by date type 1 regular expression (historische Anwendung)\n        31.01.2004\n        ca.31.01.2004\n        2004\n        ca.2004\n        keineAngabe\n      "Time points: the following values are possible by date type 1 regular expression (legacy application)\n        31.01.2004\n        approx.31.01.2004\n        2004\n        approx.2004\n        vMoments: the following values are possible by date type 1 regular expression (application historique)\n        31.01.2004\n        ca.31.01.2004\n        2004\n        ca.2004\n        keineAngabe'

    _MemberTypes = ( pyxb.binding.datatypes.date, pyxb.binding.datatypes.gYear, keineAngabe, )
datumTypA._CF_pattern = pyxb.binding.facets.CF_pattern()
datumTypA._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=datumTypA)
datumTypA.keine_Angabe = 'keine Angabe'           # originally keineAngabe.keine_Angabe
datumTypA._InitializeFacetMap(datumTypA._CF_pattern,
   datumTypA._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'datumTypA', datumTypA)
_module_typeBindings.datumTypA = datumTypA

# Union simple type: notizDatum
# superclasses datumTypB
class notizDatum (pyxb.binding.basis.STD_union):

    """Datum, an welchem die Notiz erfasst wurde. Datums-Tagengenauigkeit reicht (keine Std. und Sek.). Zwingendes Feld.Date on which the note was created. Date and day are sufficient (no hours and seconds). Compulsory field.Date à laquelle la notice a été cataloguée. L'indication du jour suffit (pas d'heure ni de seconde) Champ obligatoire."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'notizDatum')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 139, 2)
    _Documentation = "Datum, an welchem die Notiz erfasst wurde. Datums-Tagengenauigkeit reicht (keine Std. und Sek.). Zwingendes Feld.Date on which the note was created. Date and day are sufficient (no hours and seconds). Compulsory field.Date \xe0 laquelle la notice a \xe9t\xe9 catalogu\xe9e. L'indication du jour suffit (pas d'heure ni de seconde) Champ obligatoire."

    _MemberTypes = ( pyxb.binding.datatypes.date, pyxb.binding.datatypes.dateTime, )
notizDatum._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'notizDatum', notizDatum)
_module_typeBindings.notizDatum = notizDatum

# Atomic simple type: notizErfasser
class notizErfasser (text1):

    """Benutzer, welcher die Notiz erfasst hat. Optionales Feld.User who created the note. Optional field.Utilisateur qui a catalogué la notice. Champ facultatif."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'notizErfasser')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 149, 2)
    _Documentation = 'Benutzer, welcher die Notiz erfasst hat. Optionales Feld.User who created the note. Optional field.Utilisateur qui a catalogu\xe9 la notice. Champ facultatif.'
notizErfasser._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'notizErfasser', notizErfasser)
_module_typeBindings.notizErfasser = notizErfasser

# Atomic simple type: notizBeschreibung
class notizBeschreibung (text4):

    """Notiz i.e.S, d.h. Beschreibung. Zwingendes Feld.Notice in narrower sense, i.e. description. Compulsory field.Notice au sens strict, c.-à-d. description. Champ obligatoire"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'notizBeschreibung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 159, 2)
    _Documentation = 'Notiz i.e.S, d.h. Beschreibung. Zwingendes Feld.Notice in narrower sense, i.e. description. Compulsory field.Notice au sens strict, c.-\xe0-d. description. Champ obligatoire'
notizBeschreibung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'notizBeschreibung', notizBeschreibung)
_module_typeBindings.notizBeschreibung = notizBeschreibung

# Complex type comparable with content type EMPTY
class comparable (pyxb.binding.basis.complexTypeDefinition):
    """Complex type comparable with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'comparable')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 6, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    _ElementMap.update({

    })
    _AttributeMap.update({

    })
_module_typeBindings.comparable = comparable
Namespace.addCategoryObject('typeBinding', 'comparable', comparable)


# Complex type historischerZeitpunkt with content type ELEMENT_ONLY
class historischerZeitpunkt (pyxb.binding.basis.complexTypeDefinition):
    """Complex type historischerZeitpunkt with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'historischerZeitpunkt')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 7, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element ca uses Python identifier ca
    __ca = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ca'), 'ca', '__AbsentNamespace0_historischerZeitpunkt_ca', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), )


    ca = property(__ca.value, __ca.set, None, None)


    # Element datum uses Python identifier datum
    __datum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'datum'), 'datum', '__AbsentNamespace0_historischerZeitpunkt_datum', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6), )


    datum = property(__datum.value, __datum.set, None, None)

    _ElementMap.update({
        __ca.name() : __ca,
        __datum.name() : __datum
    })
    _AttributeMap.update({

    })
_module_typeBindings.historischerZeitpunkt = historischerZeitpunkt
Namespace.addCategoryObject('typeBinding', 'historischerZeitpunkt', historischerZeitpunkt)


# Complex type historischerZeitraum with content type ELEMENT_ONLY
class historischerZeitraum (pyxb.binding.basis.complexTypeDefinition):
    """Complex type historischerZeitraum with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'historischerZeitraum')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 14, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element von uses Python identifier von
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace0_historischerZeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace0_historischerZeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6), )


    bis = property(__bis.value, __bis.set, None, None)

    _ElementMap.update({
        __von.name() : __von,
        __bis.name() : __bis
    })
    _AttributeMap.update({

    })
_module_typeBindings.historischerZeitraum = historischerZeitraum
Namespace.addCategoryObject('typeBinding', 'historischerZeitraum', historischerZeitraum)


# Complex type zeitraum with content type ELEMENT_ONLY
class zeitraum (pyxb.binding.basis.complexTypeDefinition):
    """Complex type zeitraum with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'zeitraum')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 67, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element von uses Python identifier von
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace0_zeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace0_zeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6), )


    bis = property(__bis.value, __bis.set, None, None)

    _ElementMap.update({
        __von.name() : __von,
        __bis.name() : __bis
    })
    _AttributeMap.update({

    })
_module_typeBindings.zeitraum = zeitraum
Namespace.addCategoryObject('typeBinding', 'zeitraum', zeitraum)




historischerZeitpunkt._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ca'), ca, scope=historischerZeitpunkt, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), unicode_default='false'))

historischerZeitpunkt._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'datum'), datumTypA, scope=historischerZeitpunkt, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(historischerZeitpunkt._UseForTag(pyxb.namespace.ExpandedName(None, 'ca')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(historischerZeitpunkt._UseForTag(pyxb.namespace.ExpandedName(None, 'datum')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
historischerZeitpunkt._Automaton = _BuildAutomaton()




historischerZeitraum._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'von'), historischerZeitpunkt, scope=historischerZeitraum, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6)))

historischerZeitraum._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'bis'), historischerZeitpunkt, scope=historischerZeitraum, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(historischerZeitraum._UseForTag(pyxb.namespace.ExpandedName(None, 'von')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(historischerZeitraum._UseForTag(pyxb.namespace.ExpandedName(None, 'bis')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
historischerZeitraum._Automaton = _BuildAutomaton_()




zeitraum._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'von'), datumTypB, scope=zeitraum, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6)))

zeitraum._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'bis'), datumTypB, scope=zeitraum, location=pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(zeitraum._UseForTag(pyxb.namespace.ExpandedName(None, 'von')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(zeitraum._UseForTag(pyxb.namespace.ExpandedName(None, 'bis')), pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
zeitraum._Automaton = _BuildAutomaton_2()

