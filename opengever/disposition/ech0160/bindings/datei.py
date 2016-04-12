# ./bindings/datei.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2016-04-07 18:47:22.288768 by PyXB version 1.2.4 using Python 2.7.11.final.0
# Namespace AbsentNamespace4
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
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:65d8c99c-fce0-11e5-a76e-6c40088f2de0')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.4'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

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

# Atomic simple type: text1
class text1 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text1')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 169, 2)
    _Documentation = None
text1._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(100))
text1._InitializeFacetMap(text1._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text1', text1)

# Atomic simple type: text2
class text2 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text2')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 175, 2)
    _Documentation = None
text2._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(200))
text2._InitializeFacetMap(text2._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text2', text2)

# Atomic simple type: text3
class text3 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text3')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 181, 2)
    _Documentation = None
text3._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(1000))
text3._InitializeFacetMap(text3._CF_maxLength)
Namespace.addCategoryObject('typeBinding', 'text3', text3)

# Atomic simple type: text4
class text4 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'text4')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 187, 2)
    _Documentation = None
text4._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'text4', text4)

# Atomic simple type: idDatei
class idDatei (pyxb.binding.datatypes.ID):

    """Paketweit eindeutige ID für die Datei (technischer Primärschlüssel). Diese ID wird aus dem Dokument heraus referenziert.Unambiguous ID for the file throughout the package (technical primary key). This ID is referenced out of the document.ID univoque pour tout le paquet pour le dossier (clé primaire technique). Cette ID est référencée sur le document."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'idDatei')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 37, 2)
    _Documentation = 'Paketweit eindeutige ID f\xfcr die Datei (technischer Prim\xe4rschl\xfcssel). Diese ID wird aus dem Dokument heraus referenziert.Unambiguous ID for the file throughout the package (technical primary key). This ID is referenced out of the document.ID univoque pour tout le paquet pour le dossier (cl\xe9 primaire technique). Cette ID est r\xe9f\xe9renc\xe9e sur le document.'
idDatei._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'idDatei', idDatei)

# Atomic simple type: pruefalgorithmus
class pruefalgorithmus (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """Bezeichnung des verwendeten Prüfalgorithmus.Designation of the checksum algorithm used.Désignation de l'algorithme de contrôle utilisé"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'pruefalgorithmus')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 47, 2)
    _Documentation = "Bezeichnung des verwendeten Pr\xfcfalgorithmus.Designation of the checksum algorithm used.D\xe9signation de l'algorithme de contr\xf4le utilis\xe9"
pruefalgorithmus._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=pruefalgorithmus, enum_prefix=None)
pruefalgorithmus.MD5 = pruefalgorithmus._CF_enumeration.addEnumeration(unicode_value='MD5', tag='MD5')
pruefalgorithmus.SHA_1 = pruefalgorithmus._CF_enumeration.addEnumeration(unicode_value='SHA-1', tag='SHA_1')
pruefalgorithmus.SHA_256 = pruefalgorithmus._CF_enumeration.addEnumeration(unicode_value='SHA-256', tag='SHA_256')
pruefalgorithmus.SHA_512 = pruefalgorithmus._CF_enumeration.addEnumeration(unicode_value='SHA-512', tag='SHA_512')
pruefalgorithmus._InitializeFacetMap(pruefalgorithmus._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'pruefalgorithmus', pruefalgorithmus)

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

# Atomic simple type: notizErfasser
class notizErfasser (text1):

    """Benutzer, welcher die Notiz erfasst hat. Optionales Feld.User who created the note. Optional field.Utilisateur qui a catalogué la notice. Champ facultatif."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'notizErfasser')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 149, 2)
    _Documentation = 'Benutzer, welcher die Notiz erfasst hat. Optionales Feld.User who created the note. Optional field.Utilisateur qui a catalogu\xe9 la notice. Champ facultatif.'
notizErfasser._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'notizErfasser', notizErfasser)

# Atomic simple type: notizBeschreibung
class notizBeschreibung (text4):

    """Notiz i.e.S, d.h. Beschreibung. Zwingendes Feld.Notice in narrower sense, i.e. description. Compulsory field.Notice au sens strict, c.-à-d. description. Champ obligatoire"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'notizBeschreibung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 159, 2)
    _Documentation = 'Notiz i.e.S, d.h. Beschreibung. Zwingendes Feld.Notice in narrower sense, i.e. description. Compulsory field.Notice au sens strict, c.-\xe0-d. description. Champ obligatoire'
notizBeschreibung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'notizBeschreibung', notizBeschreibung)

# Atomic simple type: nameDatei
class nameDatei (text2):

    """Name der Datei, wie dieser im SIP/AIP/DIP erscheint (z.B. "p000001_Machbarkeitsanaly.pdf").Name of the file as it appears in the SIP/AIP/DIP (e.g. "p000001_Feasibility_Study.pdf").Nom du fichier comme il apparaît dans le SIP/AIP/DIP (p. ex.: "p000001_Machbarkeitsanaly.pdf")."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'nameDatei')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 7, 2)
    _Documentation = 'Name der Datei, wie dieser im SIP/AIP/DIP erscheint (z.B. "p000001_Machbarkeitsanaly.pdf").Name of the file as it appears in the SIP/AIP/DIP (e.g. "p000001_Feasibility_Study.pdf"\x9d).Nom du fichier comme il appara\xeet dans le SIP/AIP/DIP (p. ex.: "p000001_Machbarkeitsanaly.pdf").'
nameDatei._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'nameDatei', nameDatei)

# Atomic simple type: physischerName
class physischerName (text1):

    """Name der Datei im Filesystem.Name of the file in the file system.Nom du fichier dans le système de fichiers."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'physischerName')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 17, 2)
    _Documentation = 'Name der Datei im Filesystem.Name of the file in the file system.Nom du fichier dans le syst\xe8me de fichiers.'
physischerName._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'physischerName', physischerName)

# Atomic simple type: originalName
class originalName (text4):

    """Name des Ordners oder der Datei, wie diese in der Originalstruktur (im GEVER-System, in der Dateiablage) beim Aktenbildner geheissen hat (z.B. "Arbeitspaket" oder "Bericht.doc").Name of the folder or file as it was called in the original structure (in the GEVER system, in the file archive) at the records creator (e.g. "work package" or "Report.doc".Nom du répertoire ou du fichier, comme il a été inscrit dans la structure d'origine (dans le système GEVER, dans la collection de fichiers) par le producteur des documents (exemples: "Paquet de travail" ou "Rapport.doc")"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'originalName')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 27, 2)
    _Documentation = 'Name des Ordners oder der Datei, wie diese in der Originalstruktur (im GEVER-System, in der Dateiablage) beim Aktenbildner geheissen hat (z.B. "Arbeitspaket" oder "Bericht.doc").Name of the folder or file as it was called in the original structure (in the GEVER system, in the file archive) at the records creator (e.g. "work package"\x9d or "Report.doc"\x9d.Nom du r\xe9pertoire ou du fichier, comme il a \xe9t\xe9 inscrit dans la structure d\'origine (dans le syst\xe8me GEVER, dans la collection de fichiers) par le producteur des documents (exemples: "Paquet de travail" ou "Rapport.doc")'
originalName._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'originalName', originalName)

# Atomic simple type: pruefsumme
class pruefsumme (text3):

    """Prüfsummenwert (abhängig vom verwendeten Prüfalgorithmus).Checksum value (depending on the checksum algorithm used).Valeur de la somme de contrôle (dépendant de l'algorithme de contrôle utilisé)."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'pruefsumme')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 62, 2)
    _Documentation = "Pr\xfcfsummenwert (abh\xe4ngig vom verwendeten Pr\xfcfalgorithmus).Checksum value (depending on the checksum algorithm used).Valeur de la somme de contr\xf4le (d\xe9pendant de l'algorithme de contr\xf4le utilis\xe9)."
pruefsumme._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'pruefsumme', pruefsumme)

# Atomic simple type: eigenschaft
class eigenschaft (text4):

    """Generisches Attribut, welches im Zusammenhang mit Wert verwendet wird. Wird bspw. eine CSV-Datei abgeliefert, dann können mittels Attributpaar "eigenschaft" und "wert" Feld- und Zeilendelemiter, Texterkennungszeichen oder Spaltennamen angegeben werden.Generic attribute used in connection with value. For example, if a CSV file is submitted, the "property" and "value" pair of attributes can be used to indicate field and line delimiters, text recognition symbols or column names.Attribut générique qui est employé en rapport avec la valeur. Par exemple est versé un fichier CSV; ensuite, le séparateur de champs et de lignes, la reconnaissance de caractères et les noms des colonnes peuvent être indiqués au moyen de la paire d'attributs "propriétés" et "valeur"."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'eigenschaft')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/datei.xsd', 72, 2)
    _Documentation = 'Generisches Attribut, welches im Zusammenhang mit Wert verwendet wird. Wird bspw. eine CSV-Datei abgeliefert, dann k\xf6nnen mittels Attributpaar "eigenschaft" und "wert" Feld- und Zeilendelemiter, Texterkennungszeichen oder Spaltennamen angegeben werden.Generic attribute used in connection with value. For example, if a CSV file is submitted, the "property"\x9d and "value"\x9d pair of attributes can be used to indicate field and line delimiters, text recognition symbols or column names.Attribut g\xe9n\xe9rique qui est employ\xe9 en rapport avec la valeur. Par exemple est vers\xe9 un fichier CSV; ensuite, le s\xe9parateur de champs et de lignes, la reconnaissance de caract\xe8res et les noms des colonnes peuvent \xeatre indiqu\xe9s au moyen de la paire d\'attributs "propri\xe9t\xe9s" et "valeur".'
eigenschaft._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'eigenschaft', eigenschaft)

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
    __ca = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ca'), 'ca', '__AbsentNamespace4_historischerZeitpunkt_ca', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), )


    ca = property(__ca.value, __ca.set, None, None)


    # Element datum uses Python identifier datum
    __datum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'datum'), 'datum', '__AbsentNamespace4_historischerZeitpunkt_datum', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6), )


    datum = property(__datum.value, __datum.set, None, None)

    _ElementMap.update({
        __ca.name() : __ca,
        __datum.name() : __datum
    })
    _AttributeMap.update({

    })
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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace4_historischerZeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace4_historischerZeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6), )


    bis = property(__bis.value, __bis.set, None, None)

    _ElementMap.update({
        __von.name() : __von,
        __bis.name() : __bis
    })
    _AttributeMap.update({

    })
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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace4_zeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace4_zeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6), )


    bis = property(__bis.value, __bis.set, None, None)

    _ElementMap.update({
        __von.name() : __von,
        __bis.name() : __bis
    })
    _AttributeMap.update({

    })
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

