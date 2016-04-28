# ./bindings/provenienz.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2016-04-16 12:49:30.774185 by PyXB version 1.2.5-DEV using Python 2.7.11.final.0
# Namespace AbsentNamespace11
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

# Atomic simple type: aktenbildnerName
class aktenbildnerName (text2):

    """Bezeichnung der Stelle, der Organisationseinheit oder der Person(en), welche die Unterlagen oder die Datensammlung erstellt oder geführt hat. Falls der Aktenbildner unbekannt ist, muss die Angabe "Aktenbildner unbekannt" eingetragen werden.Designation of the authority, organisational unit or person(s) that created or managed the documents or the data collection. If the records creator is unknown, the information "Records creator unknown" must be entered.Désignation du service, de l'unité organisationnelle ou de la (des) personne(s), qui a créé ou géré les documents ou la collection de données. Dans le cas où le producteur de dossiers est inconnu, l'indication "producteur de dossiers inconnu" doit être inscrite."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'aktenbildnerName')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 7, 2)
    _Documentation = 'Bezeichnung der Stelle, der Organisationseinheit oder der Person(en), welche die Unterlagen oder die Datensammlung erstellt oder gef\xfchrt hat. Falls der Aktenbildner unbekannt ist, muss die Angabe "Aktenbildner unbekannt" eingetragen werden.Designation of the authority, organisational unit or person(s) that created or managed the documents or the data collection. If the records creator is unknown, the information "Records creator unknown"\x9d must be entered.D\xe9signation du service, de l\'unit\xe9 organisationnelle ou de la (des) personne(s), qui a cr\xe9\xe9 ou g\xe9r\xe9 les documents ou la collection de donn\xe9es. Dans le cas o\xf9 le producteur de dossiers est inconnu, l\'indication "producteur de dossiers inconnu" doit \xeatre inscrite.'
aktenbildnerName._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'aktenbildnerName', aktenbildnerName)
_module_typeBindings.aktenbildnerName = aktenbildnerName

# Atomic simple type: systemName
class systemName (text3):

    """Name des Informationssystems, aus dem die abgelieferten Daten (FILES), Dossiers und Dokumente (GEVER) stammen.Name of the information system from which the data (FILES), dossiers and documents (GEVER) submitted come.Nom du système d'information duquel proviennent les données (FILES), les dossiers et les documents (GEVER) versés."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'systemName')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 17, 2)
    _Documentation = "Name des Informationssystems, aus dem die abgelieferten Daten (FILES), Dossiers und Dokumente (GEVER) stammen.Name of the information system from which the data (FILES), dossiers and documents (GEVER) submitted come.Nom du syst\xe8me d'information duquel proviennent les donn\xe9es (FILES), les dossiers et les documents (GEVER) vers\xe9s."
systemName._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'systemName', systemName)
_module_typeBindings.systemName = systemName

# Atomic simple type: systemBeschreibung
class systemBeschreibung (text4):

    """Knappe Beschreibung des Informationssystems, aus dem die abgelieferten Daten (FILES) stammen. Die Beschreibung gibt Auskunft über den Zweck (inkl. Angabe der gesetzlichen Grundlagen), die Architektur, die Entwicklung und über relevante Ergänzungen und Änderungen des Systems. Zudem können hier Angaben zur Datenerhebung und zu den Organisationseinheiten gemacht werden, die neben dem Aktenbildner das System verwenden.Brief description of the information system from which the data (FILES) submitted come. The description provides information on the purpose (including an indication of the legal bases), architecture and development of the system as well as relevant additions and changes. Information on data gathering and the organisational units that use the system in addition to the records creator can also be supplied here.Description concise du système d'information duquel proviennent les données (FILES) versées. La description renseigne sur le but (y compris l'indication des bases légales), l'architecture, le développement et sur les compléments et modifications importants du système. En outre, les indications sur la collecte des données et sur les unités organisationnelles, qui emploient le système en dehors du producteur de dossiers, peuvent être données ici."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'systemBeschreibung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 27, 2)
    _Documentation = "Knappe Beschreibung des Informationssystems, aus dem die abgelieferten Daten (FILES) stammen. Die Beschreibung gibt Auskunft \xfcber den Zweck (inkl. Angabe der gesetzlichen Grundlagen), die Architektur, die Entwicklung und \xfcber relevante Erg\xe4nzungen und \xc4nderungen des Systems. Zudem k\xf6nnen hier Angaben zur Datenerhebung und zu den Organisationseinheiten gemacht werden, die neben dem Aktenbildner das System verwenden.Brief description of the information system from which the data (FILES) submitted come. The description provides information on the purpose (including an indication of the legal bases), architecture and development of the system as well as relevant additions and changes. Information on data gathering and the organisational units that use the system in addition to the records creator can also be supplied here.Description concise du syst\xe8me d'information duquel proviennent les donn\xe9es (FILES) vers\xe9es. La description renseigne sur le but (y compris l'indication des bases l\xe9gales), l'architecture, le d\xe9veloppement et sur les compl\xe9ments et modifications importants du syst\xe8me. En outre, les indications sur la collecte des donn\xe9es et sur les unit\xe9s organisationnelles, qui emploient le syst\xe8me en dehors du producteur de dossiers, peuvent \xeatre donn\xe9es ici."
systemBeschreibung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'systemBeschreibung', systemBeschreibung)
_module_typeBindings.systemBeschreibung = systemBeschreibung

# Atomic simple type: verwandteSysteme
class verwandteSysteme (text4):

    """Systeme, die mit dem beschriebenen System Daten ausgetauscht haben und damit Subsysteme, Parallelsysteme oder übergeordnete Systeme sind. Hier werden die Bezeichnungen der Systeme und die Art der Verwandtschaft eingetragen.Brief description of the information system from which the data (FILES) submitted come. The description provides information on the purpose (including an indication of the legal bases), architecture and development of the system as well as relevant additions and changes. Information on data gathering and the organisational units that use the system in addition to the records creator can also be supplied here.Systèmes qui ont échangé des données avec le système décrit et qui sont ainsi des sous-systèmes, des systèmes parallèles ou des systèmes supérieurs. Ici sont reportées les désignations des systèmes et leur relation."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'verwandteSysteme')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 37, 2)
    _Documentation = 'Systeme, die mit dem beschriebenen System Daten ausgetauscht haben und damit Subsysteme, Parallelsysteme oder \xfcbergeordnete Systeme sind. Hier werden die Bezeichnungen der Systeme und die Art der Verwandtschaft eingetragen.Brief description of the information system from which the data (FILES) submitted come. The description provides information on the purpose (including an indication of the legal bases), architecture and development of the system as well as relevant additions and changes. Information on data gathering and the organisational units that use the system in addition to the records creator can also be supplied here.Syst\xe8mes qui ont \xe9chang\xe9 des donn\xe9es avec le syst\xe8me d\xe9crit et qui sont ainsi des sous-syst\xe8mes, des syst\xe8mes parall\xe8les ou des syst\xe8mes sup\xe9rieurs. Ici sont report\xe9es les d\xe9signations des syst\xe8mes et leur relation.'
verwandteSysteme._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'verwandteSysteme', verwandteSysteme)
_module_typeBindings.verwandteSysteme = verwandteSysteme

# Atomic simple type: archivierungsmodusLoeschvorschriften
class archivierungsmodusLoeschvorschriften (text4):

    """Angaben darüber, auf welche Weise die Daten aus dem System archiviert werden, allfällige Löschvorschriften, Angaben darüber, welche Funktionalitäten des Originalsystems nicht archiviert werden konnten, und vereinbartes Intervall der Ablieferungen sind hier zu nennen.Information about the way in which the data from the system are archived, any rules on deletion, information about which functionalities of the original system could not be archived, and the agreed interval for submissions are to be indicated here.Informations sur la manière dont sont archivées les données du système, sur les éventuelles directives d'effacement, sur la fonctionnalité du système original qui ne peut pas être archivée, et sur l'intervalle convenu de versement sont ici à indiquer."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'archivierungsmodusLoeschvorschriften')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 47, 2)
    _Documentation = "Angaben dar\xfcber, auf welche Weise die Daten aus dem System archiviert werden, allf\xe4llige L\xf6schvorschriften, Angaben dar\xfcber, welche Funktionalit\xe4ten des Originalsystems nicht archiviert werden konnten, und vereinbartes Intervall der Ablieferungen sind hier zu nennen.Information about the way in which the data from the system are archived, any rules on deletion, information about which functionalities of the original system could not be archived, and the agreed interval for submissions are to be indicated here.Informations sur la mani\xe8re dont sont archiv\xe9es les donn\xe9es du syst\xe8me, sur les \xe9ventuelles directives d'effacement, sur la fonctionnalit\xe9 du syst\xe8me original qui ne peut pas \xeatre archiv\xe9e, et sur l'intervalle convenu de versement sont ici \xe0 indiquer."
archivierungsmodusLoeschvorschriften._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'archivierungsmodusLoeschvorschriften', archivierungsmodusLoeschvorschriften)
_module_typeBindings.archivierungsmodusLoeschvorschriften = archivierungsmodusLoeschvorschriften

# Atomic simple type: registratur
class registratur (text2):

    """Name der Ablage, für welche das primäre Ordnungssystem verwendet wird und die einem Mandanten im System entspricht. Eine aktenbildende Stelle kann im Prinzip mehr als eine Registratur führen. Pro Registratur gibt es allerdings nur ein primäres Ordnungssystem.Name of the archive for which the primary classification system is used and that corresponds to a client in the system. In principle, a records-creating authority may maintain more than one registry. However, there is only one primary classification system for each registry.Nom de l’archivage pour lequel le système de classement primaire est utilisé et qui correspond à un mandant dans le système. Un service qui crée des dossiers peut, en principe, gérer plus qu’un enregistrement. Par enregistrement toutefois, il n’y a qu’un système de classement primaire."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'registratur')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 57, 2)
    _Documentation = 'Name der Ablage, f\xfcr welche das prim\xe4re Ordnungssystem verwendet wird und die einem Mandanten im System entspricht. Eine aktenbildende Stelle kann im Prinzip mehr als eine Registratur f\xfchren. Pro Registratur gibt es allerdings nur ein prim\xe4res Ordnungssystem.Name of the archive for which the primary classification system is used and that corresponds to a client in the system. In principle, a records-creating authority may maintain more than one registry. However, there is only one primary classification system for each registry.Nom de l\u2019archivage pour lequel le syst\xe8me de classement primaire est utilis\xe9 et qui correspond \xe0 un mandant dans le syst\xe8me. Un service qui cr\xe9e des dossiers peut, en principe, g\xe9rer plus qu\u2019un enregistrement. Par enregistrement toutefois, il n\u2019y a qu\u2019un syst\xe8me de classement primaire.'
registratur._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'registratur', registratur)
_module_typeBindings.registratur = registratur

# Atomic simple type: geschichteAktenbildner
class geschichteAktenbildner (text4):

    """Allgemeiner Überblick über die Geschichte des Aktenbildners und Angaben über Vorgänger und Nachfolgerorganisationen.General overview of the history of the records creator and information about predecessor and successor organisations.Aperçu général sur l'histoire du service producteur de documents et indications sur les prédécesseurs et les organisations ayant pris la suite."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'geschichteAktenbildner')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 67, 2)
    _Documentation = "Allgemeiner \xdcberblick \xfcber die Geschichte des Aktenbildners und Angaben \xfcber Vorg\xe4nger und Nachfolgerorganisationen.General overview of the history of the records creator and information about predecessor and successor organisations.Aper\xe7u g\xe9n\xe9ral sur l'histoire du service producteur de documents et indications sur les pr\xe9d\xe9cesseurs et les organisations ayant pris la suite."
geschichteAktenbildner._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'geschichteAktenbildner', geschichteAktenbildner)
_module_typeBindings.geschichteAktenbildner = geschichteAktenbildner

# Atomic simple type: bemerkungProvenienz
class bemerkungProvenienz (text4):

    """Zusätzliche Informationen, die den Aktenbildner und die Herkunft der Unterlagen oder der Datensammlung betreffen.Additional information relating to the records creator and the origin of the documents or the data collection.Informations complémentaires, qui concernent le producteur de dossiers et la provenance des documents ou de la collection de données."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bemerkungProvenienz')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/provenienz.xsd', 77, 2)
    _Documentation = 'Zus\xe4tzliche Informationen, die den Aktenbildner und die Herkunft der Unterlagen oder der Datensammlung betreffen.Additional information relating to the records creator and the origin of the documents or the data collection.Informations compl\xe9mentaires, qui concernent le producteur de dossiers et la provenance des documents ou de la collection de donn\xe9es.'
bemerkungProvenienz._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bemerkungProvenienz', bemerkungProvenienz)
_module_typeBindings.bemerkungProvenienz = bemerkungProvenienz

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
    __ca = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ca'), 'ca', '__AbsentNamespace11_historischerZeitpunkt_ca', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), )


    ca = property(__ca.value, __ca.set, None, None)


    # Element datum uses Python identifier datum
    __datum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'datum'), 'datum', '__AbsentNamespace11_historischerZeitpunkt_datum', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace11_historischerZeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace11_historischerZeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace11_zeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace11_zeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6), )


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

