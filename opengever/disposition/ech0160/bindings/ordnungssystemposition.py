# ./bindings/ordnungssystemposition.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2016-04-16 12:49:30.772876 by PyXB version 1.2.5-DEV using Python 2.7.11.final.0
# Namespace AbsentNamespace9
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

# Atomic simple type: idOrdnungssystemposition
class idOrdnungssystemposition (pyxb.binding.datatypes.ID):

    """Paketweit eindeutige ID (Primärschlüssel).Unambiguous ID for the whole package (primary key).ID univoque pour tout le paquet (clé primaire)."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'idOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 27, 2)
    _Documentation = 'Paketweit eindeutige ID (Prim\xe4rschl\xfcssel).Unambiguous ID for the whole package (primary key).ID univoque pour tout le paquet (cl\xe9 primaire).'
idOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'idOrdnungssystemposition', idOrdnungssystemposition)
_module_typeBindings.idOrdnungssystemposition = idOrdnungssystemposition

# Atomic simple type: datenschutzOrdnungssystemposition
class datenschutzOrdnungssystemposition (pyxb.binding.datatypes.boolean):

    """Markierung, die angibt, ob sich in den Unterlagen der Ordnungssystemposition solche mit besonders schützenswerten Personendaten oder Persönlichkeitsprofilen gemäss Datenschutzgesetz.Marking indicating whether documents in the classification system position contain sensitive personal data or personal profiles under the Data Protection Act.Marque qui précise si des documents de la position du système de classement contiennent des données sensibles ou des profils de la personnalité selon la loi sur la protection des données."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'datenschutzOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 89, 2)
    _Documentation = 'Markierung, die angibt, ob sich in den Unterlagen der Ordnungssystemposition solche mit besonders sch\xfctzenswerten Personendaten oder Pers\xf6nlichkeitsprofilen gem\xe4ss Datenschutzgesetz.Marking indicating whether documents in the classification system position contain sensitive personal data or personal profiles under the Data Protection Act.Marque qui pr\xe9cise si des documents de la position du syst\xe8me de classement contiennent des donn\xe9es sensibles ou des profils de la personnalit\xe9 selon la loi sur la protection des donn\xe9es.'
datenschutzOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'datenschutzOrdnungssystemposition', datenschutzOrdnungssystemposition)
_module_typeBindings.datenschutzOrdnungssystemposition = datenschutzOrdnungssystemposition

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

# Atomic simple type: nummer
class nummer (text1):

    """Eindeutige Identifikation und Ordnungsmerkmal der Ordnungssystemposition.Unambiguous identification and classification feature of the classification system position.Identification univoque et caractéristique de classement de la position du système de classement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'nummer')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 7, 2)
    _Documentation = 'Eindeutige Identifikation und Ordnungsmerkmal der Ordnungssystemposition.Unambiguous identification and classification feature of the classification system position.Identification univoque et caract\xe9ristique de classement de la position du syst\xe8me de classement.'
nummer._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'nummer', nummer)
_module_typeBindings.nummer = nummer

# Atomic simple type: titelOrdnungssystemposition
class titelOrdnungssystemposition (text2):

    """Bezeichnung des Aufgabenbereichs, dem die Ordnungssystemposition zugewiesen ist.Designation of the area of responsibility to which the classification system position is allocated.Désignation du secteur d'activités qui est attribué à cette position du système de classement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'titelOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 17, 2)
    _Documentation = "Bezeichnung des Aufgabenbereichs, dem die Ordnungssystemposition zugewiesen ist.Designation of the area of responsibility to which the classification system position is allocated.D\xe9signation du secteur d'activit\xe9s qui est attribu\xe9 \xe0 cette position du syst\xe8me de classement."
titelOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'titelOrdnungssystemposition', titelOrdnungssystemposition)
_module_typeBindings.titelOrdnungssystemposition = titelOrdnungssystemposition

# Atomic simple type: federfuehrendeOrganisationseinheitOrdnungssystemposition
class federfuehrendeOrganisationseinheitOrdnungssystemposition (text2):

    """Bestimmung der für die Erledigung des Geschäftes zuständigen federführenden Organisationseinheit.Name of the lead organisational unit responsible for dealing with the business matter.Désignation de l'unité organisationnelle responsable pour le traitement de l'affaire."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'federfuehrendeOrganisationseinheitOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 37, 2)
    _Documentation = "Bestimmung der f\xfcr die Erledigung des Gesch\xe4ftes zust\xe4ndigen federf\xfchrenden Organisationseinheit.Name of the lead organisational unit responsible for dealing with the business matter.D\xe9signation de l'unit\xe9 organisationnelle responsable pour le traitement de l'affaire."
federfuehrendeOrganisationseinheitOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'federfuehrendeOrganisationseinheitOrdnungssystemposition', federfuehrendeOrganisationseinheitOrdnungssystemposition)
_module_typeBindings.federfuehrendeOrganisationseinheitOrdnungssystemposition = federfuehrendeOrganisationseinheitOrdnungssystemposition

# Atomic simple type: schutzfristenkategorieOrdnungssystemposition
class schutzfristenkategorieOrdnungssystemposition (text1):

    """Artikel des Gesetztes, der die Schutzfrist festhält, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Article of the ArchA stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristenkategorieOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 47, 2)
    _Documentation = 'Artikel des Gesetztes, der die Schutzfrist festh\xe4lt, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Article of the ArchA stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristenkategorieOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'schutzfristenkategorieOrdnungssystemposition', schutzfristenkategorieOrdnungssystemposition)
_module_typeBindings.schutzfristenkategorieOrdnungssystemposition = schutzfristenkategorieOrdnungssystemposition

# Atomic simple type: schutzfristOrdnungssystemposition
class schutzfristOrdnungssystemposition (text1):

    """Dauer der Schutzfrist in Jahren, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Durée en années du délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 57, 2)
    _Documentation = 'Dauer der Schutzfrist in Jahren, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Dur\xe9e en ann\xe9es du d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristOrdnungssystemposition._CF_pattern = pyxb.binding.facets.CF_pattern()
schutzfristOrdnungssystemposition._CF_pattern.addPattern(pattern='[0-9]*')
schutzfristOrdnungssystemposition._InitializeFacetMap(schutzfristOrdnungssystemposition._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'schutzfristOrdnungssystemposition', schutzfristOrdnungssystemposition)
_module_typeBindings.schutzfristOrdnungssystemposition = schutzfristOrdnungssystemposition

# Atomic simple type: schutzfristenBegruendungOrdnungssystemposition
class schutzfristenBegruendungOrdnungssystemposition (text4):

    """Erläuterung der Begründung für eine verlängerte Schutzfrist für Unterlagen, die nach Personennamen erschlossen sind und schützenswerte Personendaten gemäss DSG enthalten (z.B. Art. 11 BGA), und für bestimmte Kategorien oder für einzelne Dossiers, die überwiegend schutzwürdige öffentliche oder private Interessen tangieren (z.B. Art. 12 Abs. 1 BGA und Art. 12 Abs. 2 BGA).Explanation of the reasons for an extended closure period for documents that are catalogued by individuals"™ names and contain sensitive personal data in accordance with the DPA (Art. 11 ArchA) and for certain categories or individual dossiers that touch on matters where there is an overriding public or private interest in preventing consultation (Art. 12 para. 1 ArchA and Art. 12 para. 2 ArchA).Explication du motif de prolongation du délai de protection pour les documents classés selon des noms de personnes et contenant des données personnelles sensibles selon la LPD (par exemple art. 11 LAr) et pour des catégories définies ou pour certains dossiers qui touchent un intérêt public ou privé prépondérant, digne de protection (par exemple art. 12 al. 1 LAr et art. 12 al. 2 LAr)"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristenBegruendungOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 69, 2)
    _Documentation = 'Erl\xe4uterung der Begr\xfcndung f\xfcr eine verl\xe4ngerte Schutzfrist f\xfcr Unterlagen, die nach Personennamen erschlossen sind und sch\xfctzenswerte Personendaten gem\xe4ss DSG enthalten (z.B. Art. 11 BGA), und f\xfcr bestimmte Kategorien oder f\xfcr einzelne Dossiers, die \xfcberwiegend schutzw\xfcrdige \xf6ffentliche oder private Interessen tangieren (z.B. Art. 12 Abs. 1 BGA und Art. 12 Abs. 2 BGA).Explanation of the reasons for an extended closure period for documents that are catalogued by individuals"\u2122 names and contain sensitive personal data in accordance with the DPA (Art. 11 ArchA) and for certain categories or individual dossiers that touch on matters where there is an overriding public or private interest in preventing consultation (Art. 12 para. 1 ArchA and Art. 12 para. 2 ArchA).Explication du motif de prolongation du d\xe9lai de protection pour les documents class\xe9s selon des noms de personnes et contenant des donn\xe9es personnelles sensibles selon la LPD (par exemple art. 11 LAr) et pour des cat\xe9gories d\xe9finies ou pour certains dossiers qui touchent un int\xe9r\xeat public ou priv\xe9 pr\xe9pond\xe9rant, digne de protection (par exemple art. 12 al. 1 LAr et art. 12 al. 2 LAr)'
schutzfristenBegruendungOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'schutzfristenBegruendungOrdnungssystemposition', schutzfristenBegruendungOrdnungssystemposition)
_module_typeBindings.schutzfristenBegruendungOrdnungssystemposition = schutzfristenBegruendungOrdnungssystemposition

# Atomic simple type: klassifizierungskategorieOrdnungssystemposition
class klassifizierungskategorieOrdnungssystemposition (text2):

    """Grad, in dem alle der Ordnungssystemposition untergeordneten Objekte Dossier und Dokumente vor unberechtigter Einsicht geschützt werden müssen. Referenz: Verordnung vom 10.12.1990 über die Klassifizierung und Behandlung von Informationen im zivilen Verwaltungsbereich ([SR 172.015]) und Verordnung vom 1.5.1990 über den Schutz militärischer Informationen ([SR 510.411]).Degree to which all the dossier and document objects subordinated to the classification system position must be protected against unauthorised access. Reference: Ordinance of 10.12.1990 on the Classification and Treatment of Information in the Civil Administration ([SR 172.015]) and Ordinance of 1.5.1990 on the Protection of Military Information ([SR 510.411]).Degré dans lequel doivent être protégés d'une consultation non autorisée tous les dossiers et documents subordonnés à une position du système de classement. Référence: Ordonnance du 10.12.1990 sur la classification et le traitement d'informations de l'administration civile  ([SR 172.015]) et ordonnance du 1.5.1990 sur la protection des informations militaires ([SR 510.411]"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'klassifizierungskategorieOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 79, 2)
    _Documentation = "Grad, in dem alle der Ordnungssystemposition untergeordneten Objekte Dossier und Dokumente vor unberechtigter Einsicht gesch\xfctzt werden m\xfcssen. Referenz: Verordnung vom 10.12.1990 \xfcber die Klassifizierung und Behandlung von Informationen im zivilen Verwaltungsbereich ([SR 172.015]) und Verordnung vom 1.5.1990 \xfcber den Schutz milit\xe4rischer Informationen ([SR 510.411]).Degree to which all the dossier and document objects subordinated to the classification system position must be protected against unauthorised access. Reference: Ordinance of 10.12.1990 on the Classification and Treatment of Information in the Civil Administration ([SR 172.015]) and Ordinance of 1.5.1990 on the Protection of Military Information ([SR 510.411]).Degr\xe9 dans lequel doivent \xeatre prot\xe9g\xe9s d'une consultation non autoris\xe9e tous les dossiers et documents subordonn\xe9s \xe0 une position du syst\xe8me de classement. R\xe9f\xe9rence: Ordonnance du 10.12.1990 sur la classification et le traitement d'informations de l'administration civile  ([SR 172.015]) et ordonnance du 1.5.1990 sur la protection des informations militaires ([SR 510.411]"
klassifizierungskategorieOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'klassifizierungskategorieOrdnungssystemposition', klassifizierungskategorieOrdnungssystemposition)
_module_typeBindings.klassifizierungskategorieOrdnungssystemposition = klassifizierungskategorieOrdnungssystemposition

# Atomic simple type: oeffentlichkeitsstatusOrdnungssystemposition
class oeffentlichkeitsstatusOrdnungssystemposition (text2):

    """Angabe, ob der Ordnungssystemposition untergeordnete Dossiers gemäss [BGÖ] schützenswerte Dokumente enthalten oder nicht.Indication of whether or not dossiers subordinated to the classification system position contain sensitive documents under the [FoIA].Indiquer si les dossiers subordonnés à la position du système de classement contiennent ou non des documents dignes de protection selon la [LTrans]"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'oeffentlichkeitsstatusOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 99, 2)
    _Documentation = 'Angabe, ob der Ordnungssystemposition untergeordnete Dossiers gem\xe4ss [BG\xd6] sch\xfctzenswerte Dokumente enthalten oder nicht.Indication of whether or not dossiers subordinated to the classification system position contain sensitive documents under the [FoIA].Indiquer si les dossiers subordonn\xe9s \xe0 la position du syst\xe8me de classement contiennent ou non des documents dignes de protection selon la [LTrans]'
oeffentlichkeitsstatusOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'oeffentlichkeitsstatusOrdnungssystemposition', oeffentlichkeitsstatusOrdnungssystemposition)
_module_typeBindings.oeffentlichkeitsstatusOrdnungssystemposition = oeffentlichkeitsstatusOrdnungssystemposition

# Atomic simple type: oeffentlichkeitsstatusBegruendungOrdnungssystemposition
class oeffentlichkeitsstatusBegruendungOrdnungssystemposition (text4):

    """Argumente gegen die öffentliche Zugänglichkeit gemäss [BGÖ]. Gemäss Entwurf [BGÖ] muss begründet werden, warum Unterlagen nicht öffentlich zugänglich gemacht werden können.Arguments against public access under the [FoIA]. According to the draft [FoIA], reasons why documents cannot be made publicly accessible must be stated.Arguments contre l'accès public selon la [LTrans]. Selon le projet de [LTrans], il faut donner les raisons pour lesquelles des documents ne peuvent être accessibles au public."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'oeffentlichkeitsstatusBegruendungOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 109, 2)
    _Documentation = "Argumente gegen die \xf6ffentliche Zug\xe4nglichkeit gem\xe4ss [BG\xd6]. Gem\xe4ss Entwurf [BG\xd6] muss begr\xfcndet werden, warum Unterlagen nicht \xf6ffentlich zug\xe4nglich gemacht werden k\xf6nnen.Arguments against public access under the [FoIA]. According to the draft [FoIA], reasons why documents cannot be made publicly accessible must be stated.Arguments contre l'acc\xe8s public selon la [LTrans]. Selon le projet de [LTrans], il faut donner les raisons pour lesquelles des documents ne peuvent \xeatre accessibles au public."
oeffentlichkeitsstatusBegruendungOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'oeffentlichkeitsstatusBegruendungOrdnungssystemposition', oeffentlichkeitsstatusBegruendungOrdnungssystemposition)
_module_typeBindings.oeffentlichkeitsstatusBegruendungOrdnungssystemposition = oeffentlichkeitsstatusBegruendungOrdnungssystemposition

# Atomic simple type: sonstigeBestimmungenOrdnungssystemposition
class sonstigeBestimmungenOrdnungssystemposition (text4):

    """Angaben über sonstige rechtliche Auflagen, denen die Ordnungssystemposition unterstellt ist. Information on other legal conditions to which the classification system position is subject. Informations sur d'autres éventuelles conditions légales auxquelles est soumise la position du système de classement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'sonstigeBestimmungenOrdnungssystemposition')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/ordnungssystemposition.xsd', 119, 2)
    _Documentation = "Angaben \xfcber sonstige rechtliche Auflagen, denen die Ordnungssystemposition unterstellt ist. Information on other legal conditions to which the classification system position is subject. Informations sur d'autres \xe9ventuelles conditions l\xe9gales auxquelles est soumise la position du syst\xe8me de classement."
sonstigeBestimmungenOrdnungssystemposition._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'sonstigeBestimmungenOrdnungssystemposition', sonstigeBestimmungenOrdnungssystemposition)
_module_typeBindings.sonstigeBestimmungenOrdnungssystemposition = sonstigeBestimmungenOrdnungssystemposition

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
    __ca = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ca'), 'ca', '__AbsentNamespace9_historischerZeitpunkt_ca', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), )


    ca = property(__ca.value, __ca.set, None, None)


    # Element datum uses Python identifier datum
    __datum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'datum'), 'datum', '__AbsentNamespace9_historischerZeitpunkt_datum', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace9_historischerZeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace9_historischerZeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace9_zeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace9_zeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6), )


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

