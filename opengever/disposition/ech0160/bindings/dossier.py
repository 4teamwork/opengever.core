# ./bindings/dossier.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2016-04-07 18:47:22.288390 by PyXB version 1.2.4 using Python 2.7.11.final.0
# Namespace AbsentNamespace6
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

# Atomic simple type: idDossier
class idDossier (pyxb.binding.datatypes.ID):

    """Paketweit eindeutige ID. Sie wird im AIS im Modul Verzeichnungseinheiten auf Dossierstufe verzeichnet.Unambiguous ID for the whole package. It is described in the units of description module of the AIS at dossier level.ID univoque pour tout le paquet. Elle est enregistrée dans AIS dans le module Unité de description au niveau des dossiers."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'idDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 73, 2)
    _Documentation = 'Paketweit eindeutige ID. Sie wird im AIS im Modul Verzeichnungseinheiten auf Dossierstufe verzeichnet.Unambiguous ID for the whole package. It is described in the units of description module of the AIS at dossier level.ID univoque pour tout le paquet. Elle est enregistr\xe9e dans AIS dans le module Unit\xe9 de description au niveau des dossiers.'
idDossier._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1))
idDossier._InitializeFacetMap(idDossier._CF_minLength)
Namespace.addCategoryObject('typeBinding', 'idDossier', idDossier)

# Atomic simple type: erscheinungsformDossier
class erscheinungsformDossier (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """Angaben darüber, ob das Dossier digitale, nicht-digitale (Papier, audiovisuell) oder sowohl digitale als auch nicht-digitale Dokumente enthält.Indication of whether the dossier contains digital, non-digital (paper, audiovisual) or both digital and non-digital documents.Indiquer si le dossier contient des documents numériques, non numériques (papier, audiovisuel) """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'erscheinungsformDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 85, 2)
    _Documentation = 'Angaben dar\xfcber, ob das Dossier digitale, nicht-digitale (Papier, audiovisuell) oder sowohl digitale als auch nicht-digitale Dokumente enth\xe4lt.Indication of whether the dossier contains digital, non-digital (paper, audiovisual) or both digital and non-digital documents.Indiquer si le dossier contient des documents num\xe9riques, non num\xe9riques (papier, audiovisuel) '
erscheinungsformDossier._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=erscheinungsformDossier, enum_prefix=None)
erscheinungsformDossier.keine_Angabe = erscheinungsformDossier._CF_enumeration.addEnumeration(unicode_value='keine Angabe', tag='keine_Angabe')
erscheinungsformDossier.digital = erscheinungsformDossier._CF_enumeration.addEnumeration(unicode_value='digital', tag='digital')
erscheinungsformDossier.nicht_digital = erscheinungsformDossier._CF_enumeration.addEnumeration(unicode_value='nicht digital', tag='nicht_digital')
erscheinungsformDossier.gemischt = erscheinungsformDossier._CF_enumeration.addEnumeration(unicode_value='gemischt', tag='gemischt')
erscheinungsformDossier._InitializeFacetMap(erscheinungsformDossier._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'erscheinungsformDossier', erscheinungsformDossier)

# Atomic simple type: datenschutzDossier
class datenschutzDossier (pyxb.binding.datatypes.boolean):

    """Markierung, die angibt, ob sich in den Dokumenten des Dossiers besonders schützenswerten Personendaten oder Persönlichkeitsprofilen gemäss Datenschutzrecht.Marking indicating whether documents in the dossier contain sensitive personal data or personal profiles under the Data Protection Act.Marque qui précise si des documents du dossier contiennent des données sensibles ou des profils de la personnalité selon la loi sur la protection des données"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'datenschutzDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 162, 2)
    _Documentation = 'Markierung, die angibt, ob sich in den Dokumenten des Dossiers besonders sch\xfctzenswerten Personendaten oder Pers\xf6nlichkeitsprofilen gem\xe4ss Datenschutzrecht.Marking indicating whether documents in the dossier contain sensitive personal data or personal profiles under the Data Protection Act.Marque qui pr\xe9cise si des documents du dossier contiennent des donn\xe9es sensibles ou des profils de la personnalit\xe9 selon la loi sur la protection des donn\xe9es'
datenschutzDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'datenschutzDossier', datenschutzDossier)

# Atomic simple type: orderVorgang
class orderVorgang (pyxb.binding.datatypes.integer):

    """Ordnungszahl welche die Reihenfolge von Vorgängen innerhalb eines Dossiers festlegt, muss innerhalb des selben Dossier eindeutig sein.Atomic number which defines the sequence of operations within a dossier, must be unique within the same dossier.Numéro qui définit l'ordre des activités au sein d'un dossier. Doit être univoque au sein du même dossier."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'orderVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 222, 2)
    _Documentation = "Ordnungszahl welche die Reihenfolge von Vorg\xe4ngen innerhalb eines Dossiers festlegt, muss innerhalb des selben Dossier eindeutig sein.Atomic number which defines the sequence of operations within a dossier, must be unique within the same dossier.Num\xe9ro qui d\xe9finit l'ordre des activit\xe9s au sein d'un dossier. Doit \xeatre univoque au sein du m\xeame dossier."
orderVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'orderVorgang', orderVorgang)

# Atomic simple type: orderAktivitaet
class orderAktivitaet (pyxb.binding.datatypes.integer):

    """Ordnungszahl welche die Reihenfolge der Aktivitäten innerhalb eines Vorgangs festlegt, muss innerhalb des selben Vorgangs eindeutig sein.Atomic number which defines the sequence of activities within a process, must be unique within the same process.Numéro qui définit l'ordre des activités au sein d'un processus. Doit être univoque au sein du même processus."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'orderAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 282, 2)
    _Documentation = "Ordnungszahl welche die Reihenfolge der Aktivit\xe4ten innerhalb eines Vorgangs festlegt, muss innerhalb des selben Vorgangs eindeutig sein.Atomic number which defines the sequence of activities within a process, must be unique within the same process.Num\xe9ro qui d\xe9finit l'ordre des activit\xe9s au sein d'un processus. Doit \xeatre univoque au sein du m\xeame processus."
orderAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'orderAktivitaet', orderAktivitaet)

# Union simple type: abschlussdatumAktivitaet
# superclasses pyxb.binding.datatypes.anySimpleType
class abschlussdatumAktivitaet (pyxb.binding.basis.STD_union):

    """Tag, an dem die Aktivität abgeschlossen worden ist.Day on which the activity has been completed.Jour de clôture de l'activité"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'abschlussdatumAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 322, 2)
    _Documentation = "Tag, an dem die Aktivit\xe4t abgeschlossen worden ist.Day on which the activity has been completed.Jour de cl\xf4ture de l'activit\xe9"

    _MemberTypes = ( pyxb.binding.datatypes.date, pyxb.binding.datatypes.dateTime, )
abschlussdatumAktivitaet._CF_pattern = pyxb.binding.facets.CF_pattern()
abschlussdatumAktivitaet._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=abschlussdatumAktivitaet)
abschlussdatumAktivitaet._InitializeFacetMap(abschlussdatumAktivitaet._CF_pattern,
   abschlussdatumAktivitaet._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'abschlussdatumAktivitaet', abschlussdatumAktivitaet)

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

# Atomic simple type: aktenzeichen
class aktenzeichen (text2):

    """Identifikation und Ordnungsmerkmal des Dossiers. Das Aktenzeichen erlaubt es, das Dossier innerhalb eines bestimmten Ablagesystems einer eindeutigen Position (Rubrik) des OS zuzuordnen.Identification and classification feature of the dossier. The file reference allows the dossier to be assigned to an unambiguous position (rubric) of the CS within a specific archive system.Identification et caractéristique de classement du dossier. La référence permet d'attribuer le dossier dans un système de classement déterminé à une position univoque (rubrique) du système de classement."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'aktenzeichen')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 7, 2)
    _Documentation = "Identifikation und Ordnungsmerkmal des Dossiers. Das Aktenzeichen erlaubt es, das Dossier innerhalb eines bestimmten Ablagesystems einer eindeutigen Position (Rubrik) des OS zuzuordnen.Identification and classification feature of the dossier. The file reference allows the dossier to be assigned to an unambiguous position (rubric) of the CS within a specific archive system.Identification et caract\xe9ristique de classement du dossier. La r\xe9f\xe9rence permet d'attribuer le dossier dans un syst\xe8me de classement d\xe9termin\xe9 \xe0 une position univoque (rubrique) du syst\xe8me de classement."
aktenzeichen._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'aktenzeichen', aktenzeichen)

# Atomic simple type: zusatzmerkmal
class zusatzmerkmal (text2):

    """Angaben über zusätzliche Merkmale, welche das Dossier identifizieren. Hier kann z.B. die Bandnummer eines Dossiers vermerkt werden, als Unterscheidungs- und Reihungsmerkmal von Fortsetzungsdossiers mit demselben Dossier-Titel und mit demselben Aktenzeichen erfasst.Information on additional characteristics that identify the dossier. For example the volume number of a dossier can be indicated here to differentiate and sequence in respect of consecutive dossiers with the same dossier title and the same file reference.Informations sur des composants additionnels qui servent à l'identification du dossier. Ici peut, par exemple, être mentionné le numéro de volume d'un dossier, qui constitue une caractéristique de différenciation des dossiers successifs avec le même titre et la même référence."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'zusatzmerkmal')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 17, 2)
    _Documentation = "Angaben \xfcber zus\xe4tzliche Merkmale, welche das Dossier identifizieren. Hier kann z.B. die Bandnummer eines Dossiers vermerkt werden, als Unterscheidungs- und Reihungsmerkmal von Fortsetzungsdossiers mit demselben Dossier-Titel und mit demselben Aktenzeichen erfasst.Information on additional characteristics that identify the dossier. For example the volume number of a dossier can be indicated here to differentiate and sequence in respect of consecutive dossiers with the same dossier title and the same file reference.Informations sur des composants additionnels qui servent \xe0 l'identification du dossier. Ici peut, par exemple, \xeatre mentionn\xe9 le num\xe9ro de volume d'un dossier, qui constitue une caract\xe9ristique de diff\xe9renciation des dossiers successifs avec le m\xeame titre et la m\xeame r\xe9f\xe9rence."
zusatzmerkmal._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'zusatzmerkmal', zusatzmerkmal)

# Atomic simple type: titelDossier
class titelDossier (text4):

    """Bezeichnung des Dossiers.
        GEVER: Kurzbeschreibung des Geschäftsfalls (bei Seriendossierbildung) oder des Sachbetreffs (bei Sachdossierbildung) zu welchem Dokumente im Dossier abgelegt werden.
        FILES: Kurzbeschreibung des Inhalts der Datensammlung und der Dokumentation (falls vorhanden)"Designation of the dossier.
        GEVER: Brief description of the business event (when creating serial dossiers) or matter (when creating dossiers for specific matters) in respect of which documents are archived in the dossier.
        FILES: Brief description of the content of the data collection and the documentation (if present)''Désignation du dossier ou du groupe de documents.
        GEVER: brève description de l'affaire (dans le cas de la formation des dossiers en série) ou des objets (dans le cas de la formation de dossiers) auxquels appartiennent les documents classés dans le dossier.
        FILES: brève description du contenu de la collection de données et de la documentation (si elle existe)." """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'titelDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 27, 2)
    _Documentation = 'Bezeichnung des Dossiers.\n        GEVER: Kurzbeschreibung des Gesch\xe4ftsfalls (bei Seriendossierbildung) oder des Sachbetreffs (bei Sachdossierbildung) zu welchem Dokumente im Dossier abgelegt werden. \n        FILES: Kurzbeschreibung des Inhalts der Datensammlung und der Dokumentation (falls vorhanden)"Designation of the dossier.\n        GEVER: Brief description of the business event (when creating serial dossiers) or matter (when creating dossiers for specific matters) in respect of which documents are archived in the dossier. \n        FILES: Brief description of the content of the data collection and the documentation (if present)""D\xe9signation du dossier ou du groupe de documents.\n        GEVER: br\xe8ve description de l\'affaire (dans le cas de la formation des dossiers en s\xe9rie) ou des objets (dans le cas de la formation de dossiers) auxquels appartiennent les documents class\xe9s dans le dossier.\n        FILES: br\xe8ve description du contenu de la collection de donn\xe9es et de la documentation (si elle existe)."'
titelDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'titelDossier', titelDossier)

# Atomic simple type: inhalt
class inhalt (text4):

    """Inhaltlicher Schwerpunkt der Datensammlung sofern dies nicht aus dem Feld "Titel" hervorgeht.Main content focus of the data collection, if not clear from the "title" field.Sujet principal du contenu de la collection de données, si celui-ci n'apparaît pas dans le champ "Titre"."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'inhalt')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 43, 2)
    _Documentation = 'Inhaltlicher Schwerpunkt der Datensammlung sofern dies nicht aus dem Feld "Titel" hervorgeht.Main content focus of the data collection, if not clear from the "title"\x9d field.Sujet principal du contenu de la collection de donn\xe9es, si celui-ci n\'appara\xeet pas dans le champ "Titre".'
inhalt._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'inhalt', inhalt)

# Atomic simple type: formInhalt
class formInhalt (text4):

    """Angabe des Mediums (Fotos, Tondokumente, schriftliche Unterlagen usw.)Indication of the medium (photos, sound documents, written documents, etc.)Indication du support (photos, documents sonores, documents manuscrits, etc.)"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'formInhalt')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 53, 2)
    _Documentation = 'Angabe des Mediums (Fotos, Tondokumente, schriftliche Unterlagen usw.)Indication of the medium (photos, sound documents, written documents, etc.)Indication du support (photos, documents sonores, documents manuscrits, etc.)'
formInhalt._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'formInhalt', formInhalt)

# Atomic simple type: umfang
class umfang (text4):

    """Anzahl der Dateien des Dossiers und Umfang in MBytes zum Zeitpunkt der Ablieferung. Bei Datenbanken: Anzahl Datensätze der vorliegenden Datensammlung zum Zeitpunkt der Ablieferung. Als Datensatz gilt das Ensemble von Zeilen einer oder mehrerer miteinander verknüpften Tabellen (zentrale logische Einheit). Die Anzahl Datensätze ist zusammen mit der Bezeichnung der zentralen logischen Einheit zu nennen. Diese hängt vom Hauptfokus der Datensammlung ab. Bei Unklarheit muss mit einem Zusatztext erklärt werden, wie viele Datensätze welchen Typs vorliegen.Number of files in the dossier and size in MBytes at the time of submission. For databases: number of datasets in the present data collection at the time of submission. A dataset is a set of lines of one or more interlinked tables (central logical unit). The number of datasets must be named along with the designation of the central logical unit. This depends on the main focus of the data collection. Where there is uncertainty, an additional text must be supplied to explain how many datasets of which type are present.Nombre de fichiers dans le dossier et volume en MBytes au moment du versement. Pour les bases de données: nombre de données dans la collection de données au moment du versement. La notion donnée s'applique à l'ensemble des lignes d'un ou de plusieurs tableaux liés l'un à l'autre (unité logique centrale). Le nombre de données est à mentionner avec la désignation de l'unité logique centrale. Ceci dépend du sujet principal de la collection de données. En cas de manque de clarté doit être indiqué combien de données existent pour chaque type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'umfang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 63, 2)
    _Documentation = "Anzahl der Dateien des Dossiers und Umfang in MBytes zum Zeitpunkt der Ablieferung. Bei Datenbanken: Anzahl Datens\xe4tze der vorliegenden Datensammlung zum Zeitpunkt der Ablieferung. Als Datensatz gilt das Ensemble von Zeilen einer oder mehrerer miteinander verkn\xfcpften Tabellen (zentrale logische Einheit). Die Anzahl Datens\xe4tze ist zusammen mit der Bezeichnung der zentralen logischen Einheit zu nennen. Diese h\xe4ngt vom Hauptfokus der Datensammlung ab. Bei Unklarheit muss mit einem Zusatztext erkl\xe4rt werden, wie viele Datens\xe4tze welchen Typs vorliegen.Number of files in the dossier and size in MBytes at the time of submission. For databases: number of datasets in the present data collection at the time of submission. A dataset is a set of lines of one or more interlinked tables (central logical unit). The number of datasets must be named along with the designation of the central logical unit. This depends on the main focus of the data collection. Where there is uncertainty, an additional text must be supplied to explain how many datasets of which type are present.Nombre de fichiers dans le dossier et volume en MBytes au moment du versement. Pour les bases de donn\xe9es: nombre de donn\xe9es dans la collection de donn\xe9es au moment du versement. La notion donn\xe9e s'applique \xe0 l'ensemble des lignes d'un ou de plusieurs tableaux li\xe9s l'un \xe0 l'autre (unit\xe9 logique centrale). Le nombre de donn\xe9es est \xe0 mentionner avec la d\xe9signation de l'unit\xe9 logique centrale. Ceci d\xe9pend du sujet principal de la collection de donn\xe9es. En cas de manque de clart\xe9 doit \xeatre indiqu\xe9 combien de donn\xe9es existent pour chaque type."
umfang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'umfang', umfang)

# Atomic simple type: federfuehrendeOrganisationseinheitDossier
class federfuehrendeOrganisationseinheitDossier (text2):

    """Bestimmung der für die Erledigung des Geschäftes zuständigen federführenden Organisationseinheit.Name of the lead organisational unit responsible for dealing with the business matter.Désignation de l'unité organisationnelle responsable pour le traitement d'une affaire."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'federfuehrendeOrganisationseinheitDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 100, 2)
    _Documentation = "Bestimmung der f\xfcr die Erledigung des Gesch\xe4ftes zust\xe4ndigen federf\xfchrenden Organisationseinheit.Name of the lead organisational unit responsible for dealing with the business matter.D\xe9signation de l'unit\xe9 organisationnelle responsable pour le traitement d'une affaire."
federfuehrendeOrganisationseinheitDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'federfuehrendeOrganisationseinheitDossier', federfuehrendeOrganisationseinheitDossier)

# Atomic simple type: entstehungszeitraumAnmerkung
class entstehungszeitraumAnmerkung (text4):

    """Zusätzliche Informationen, welche für die Ermittlung des Entstehungszeitraums relevant sind. Hier können Angaben über allfällige Löschungen und Mutationen an der Datensammlung eingetragen werden (für FILES relevant). Falls der Entstehungszeitraum geschätzt wurde, ist hier das Kriterium für die Schätzung zu nennen.Additional information relevant for determining the creation period. Information on any deletions and changes in the data collection can be entered here (relevant for FILES). If the creation period has been estimated, the criterion for the estimate is to be named here.Informations complémentaires qui sont importantes pour la détermination de la période de création. Ici peuvent être reportées les informations sur les effacements et les mutations de la collection de données (important pour FILES). Si la période de création a été estimée, le critère d'estimation est à mentionner ici."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'entstehungszeitraumAnmerkung')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 110, 2)
    _Documentation = "Zus\xe4tzliche Informationen, welche f\xfcr die Ermittlung des Entstehungszeitraums relevant sind. Hier k\xf6nnen Angaben \xfcber allf\xe4llige L\xf6schungen und Mutationen an der Datensammlung eingetragen werden (f\xfcr FILES relevant). Falls der Entstehungszeitraum gesch\xe4tzt wurde, ist hier das Kriterium f\xfcr die Sch\xe4tzung zu nennen.Additional information relevant for determining the creation period. Information on any deletions and changes in the data collection can be entered here (relevant for FILES). If the creation period has been estimated, the criterion for the estimate is to be named here.Informations compl\xe9mentaires qui sont importantes pour la d\xe9termination de la p\xe9riode de cr\xe9ation. Ici peuvent \xeatre report\xe9es les informations sur les effacements et les mutations de la collection de donn\xe9es (important pour FILES). Si la p\xe9riode de cr\xe9ation a \xe9t\xe9 estim\xe9e, le crit\xe8re d'estimation est \xe0 mentionner ici."
entstehungszeitraumAnmerkung._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'entstehungszeitraumAnmerkung', entstehungszeitraumAnmerkung)

# Atomic simple type: schutzfristenkategorieDossier
class schutzfristenkategorieDossier (text1):

    """Artikel des Gesetzes, der die Schutzfrist festhält, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Article of the law stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristenkategorieDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 120, 2)
    _Documentation = 'Artikel des Gesetzes, der die Schutzfrist festh\xe4lt, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Article of the law stipulating the closure period reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Article de la loi qui fixe le d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristenkategorieDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'schutzfristenkategorieDossier', schutzfristenkategorieDossier)

# Atomic simple type: schutzfristDossier
class schutzfristDossier (text1):

    """Dauer der Schutzfrist in Jahren, die das Amt im Formular „Meldung von Unterlagen mit besonderer Schutzfrist und öffentlich zugänglichen Unterlagen“ gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollständigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents" form and checked for formal correctness and completeness by the archive.Durée en années du délai de protection que l’administration a annoncé dans le formulaire "Annonce de documents avec un délai de protection particulier et de documents consultables par le public" et dont les archives ont contrôlé l’exactitude et l’intégralité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 130, 2)
    _Documentation = 'Dauer der Schutzfrist in Jahren, die das Amt im Formular \u201eMeldung von Unterlagen mit besonderer Schutzfrist und \xf6ffentlich zug\xe4nglichen Unterlagen\u201c gemeldet hat und vom Archiv auf ihre formale Korrektheit und Vollst\xe4ndigkeit kontrolliert worden ist.Length of the closure period in years reported by the authority in the "Notification of documents subject to a special closure period and publicly accessible documents"\x9d form and checked for formal correctness and completeness by the archive.Dur\xe9e en ann\xe9es du d\xe9lai de protection que l\u2019administration a annonc\xe9 dans le formulaire "Annonce de documents avec un d\xe9lai de protection particulier et de documents consultables par le public" et dont les archives ont contr\xf4l\xe9 l\u2019exactitude et l\u2019int\xe9gralit\xe9.'
schutzfristDossier._CF_pattern = pyxb.binding.facets.CF_pattern()
schutzfristDossier._CF_pattern.addPattern(pattern='[0-9]*')
schutzfristDossier._InitializeFacetMap(schutzfristDossier._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'schutzfristDossier', schutzfristDossier)

# Atomic simple type: schutzfristenBegruendungDossier
class schutzfristenBegruendungDossier (text4):

    """Erläuterung der Begründung für eine verlängerte Schutzfrist für Unterlagen, die nach Personennamen erschlossen sind und schützenswerte Personendaten gemäss DSG enthalten (z.B. Art. 11 BGA), und für bestimmte Kategorien oder für einzelne Dossiers, die überwiegend schutzwürdige öffentliche oder private Interessen tangieren (z.B. Art. 12 Abs. 1 BGA und Art. 12 Abs. 2 BGA).Explanation of the reasons for an extended closure period for documents that are catalogued by individuals"™ names and contain sensitive personal data in accordance with the DPA (Art. 11 ArchA) and for certain categories or individual dossiers that touch on matters where there is an overriding public or private interest in preventing consultation (Art. 12 para. 1 ArchA and Art. 12 para. 2 ArchA).Explication du motif de prolongation du délai de protection pour les documents classés selon des noms de personnes et contenant des données personnelles sensibles selon la LPD (par exemple art. 11 LAr) et pour des catégories définies ou pour certains dossiers qui touchent un intérêt public ou privé prépondérant, digne de protection (par exemple art. 12 al. 1 LAr et art. 12 al. 2 LAr)"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'schutzfristenBegruendungDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 142, 2)
    _Documentation = 'Erl\xe4uterung der Begr\xfcndung f\xfcr eine verl\xe4ngerte Schutzfrist f\xfcr Unterlagen, die nach Personennamen erschlossen sind und sch\xfctzenswerte Personendaten gem\xe4ss DSG enthalten (z.B. Art. 11 BGA), und f\xfcr bestimmte Kategorien oder f\xfcr einzelne Dossiers, die \xfcberwiegend schutzw\xfcrdige \xf6ffentliche oder private Interessen tangieren (z.B. Art. 12 Abs. 1 BGA und Art. 12 Abs. 2 BGA).Explanation of the reasons for an extended closure period for documents that are catalogued by individuals"\u2122 names and contain sensitive personal data in accordance with the DPA (Art. 11 ArchA) and for certain categories or individual dossiers that touch on matters where there is an overriding public or private interest in preventing consultation (Art. 12 para. 1 ArchA and Art. 12 para. 2 ArchA).Explication du motif de prolongation du d\xe9lai de protection pour les documents class\xe9s selon des noms de personnes et contenant des donn\xe9es personnelles sensibles selon la LPD (par exemple art. 11 LAr) et pour des cat\xe9gories d\xe9finies ou pour certains dossiers qui touchent un int\xe9r\xeat public ou priv\xe9 pr\xe9pond\xe9rant, digne de protection (par exemple art. 12 al. 1 LAr et art. 12 al. 2 LAr)'
schutzfristenBegruendungDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'schutzfristenBegruendungDossier', schutzfristenBegruendungDossier)

# Atomic simple type: klassifizierungskategorieDossier
class klassifizierungskategorieDossier (text2):

    """Grad, in dem das Dossier und die enthaltenen Dokumente und Dateien vor unberechtigter Einsicht geschützt werden müssen. Referenz: Verordnung vom 10.12.1990 über die Klassifizierung und Behandlung von Informationen im zivilen Verwaltungsbereich ([SR 172.015]) und Verordnung vom 1.5.1990 über den Schutz militärischer Informationen ([SR 510.411]).Degree to which the dossier and the documents and files it contains must be protected against unauthorised access. Reference: Ordinance of 10.12.1990 on the Classification and Treatment of Information in the Civil Administration ([SR 172.015]) and Ordinance of 1.5.1990 on the Protection of Military Information ([SR 510.411]).Degré dans lequel le dossier et les documents et fichiers qu'il contient doivent être protégés d'une consultation non autorisée. Référence: Ordonnance du 10.12.1990 sur la classification et le traitement d'informations de l'administration civile  ([SR 172.015]) et ordonnance du 1.5.1990 sur la protection des informations militaires ([SR 510.411])."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'klassifizierungskategorieDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 152, 2)
    _Documentation = "Grad, in dem das Dossier und die enthaltenen Dokumente und Dateien vor unberechtigter Einsicht gesch\xfctzt werden m\xfcssen. Referenz: Verordnung vom 10.12.1990 \xfcber die Klassifizierung und Behandlung von Informationen im zivilen Verwaltungsbereich ([SR 172.015]) und Verordnung vom 1.5.1990 \xfcber den Schutz milit\xe4rischer Informationen ([SR 510.411]).Degree to which the dossier and the documents and files it contains must be protected against unauthorised access. Reference: Ordinance of 10.12.1990 on the Classification and Treatment of Information in the Civil Administration ([SR 172.015]) and Ordinance of 1.5.1990 on the Protection of Military Information ([SR 510.411]).Degr\xe9 dans lequel le dossier et les documents et fichiers qu'il contient doivent \xeatre prot\xe9g\xe9s d'une consultation non autoris\xe9e. R\xe9f\xe9rence: Ordonnance du 10.12.1990 sur la classification et le traitement d'informations de l'administration civile  ([SR 172.015]) et ordonnance du 1.5.1990 sur la protection des informations militaires ([SR 510.411])."
klassifizierungskategorieDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'klassifizierungskategorieDossier', klassifizierungskategorieDossier)

# Atomic simple type: oeffentlichkeitsstatusDossier
class oeffentlichkeitsstatusDossier (text2):

    """Angabe, ob das Dossier gemäss [BGÖ] schützenswerte Dokumente oder Dateien enthält oder nicht.Indication of whether or not the dossier contains sensitive documents or files.Indiquer le dossier contient ou non des documents dignes de protection selon la [LTrans]."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'oeffentlichkeitsstatusDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 172, 2)
    _Documentation = 'Angabe, ob das Dossier gem\xe4ss [BG\xd6] sch\xfctzenswerte Dokumente oder Dateien enth\xe4lt oder nicht.Indication of whether or not the dossier contains sensitive documents or files.Indiquer le dossier contient ou non des documents dignes de protection selon la [LTrans].'
oeffentlichkeitsstatusDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'oeffentlichkeitsstatusDossier', oeffentlichkeitsstatusDossier)

# Atomic simple type: oeffentlichkeitsstatusBegruendungDossier
class oeffentlichkeitsstatusBegruendungDossier (text4):

    """Argumente gegen die öffentliche Zugänglichkeit gemäss [BGÖ]. Gemäss Entwurf [BGÖ] muss begründet werden, warum Unterlagen nicht öffentlich zugänglich gemacht werden können.Arguments against public access. Reasons why documents cannot be made publicly accessible must be stated.Arguments contre l'accès public selon la [LTrans]. Selon le projet de [LTrans], il faut donner les raisons pour lesquelles des documents ne peuvent être accessibles au public."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'oeffentlichkeitsstatusBegruendungDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 182, 2)
    _Documentation = "Argumente gegen die \xf6ffentliche Zug\xe4nglichkeit gem\xe4ss [BG\xd6]. Gem\xe4ss Entwurf [BG\xd6] muss begr\xfcndet werden, warum Unterlagen nicht \xf6ffentlich zug\xe4nglich gemacht werden k\xf6nnen.Arguments against public access. Reasons why documents cannot be made publicly accessible must be stated.Arguments contre l'acc\xe8s public selon la [LTrans]. Selon le projet de [LTrans], il faut donner les raisons pour lesquelles des documents ne peuvent \xeatre accessibles au public."
oeffentlichkeitsstatusBegruendungDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'oeffentlichkeitsstatusBegruendungDossier', oeffentlichkeitsstatusBegruendungDossier)

# Atomic simple type: sonstigeBestimmungenDossier
class sonstigeBestimmungenDossier (text4):

    """Angaben über sonstige rechtliche Auflagen, denen das Dossier unterstellt ist.Indication of other legal conditions to which the dossier is subject.Informations sur d'autres éventuelles conditions légales auxquelles est soumis le dossier."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'sonstigeBestimmungenDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 192, 2)
    _Documentation = "Angaben \xfcber sonstige rechtliche Auflagen, denen das Dossier unterstellt ist.Indication of other legal conditions to which the dossier is subject.Informations sur d'autres \xe9ventuelles conditions l\xe9gales auxquelles est soumis le dossier."
sonstigeBestimmungenDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'sonstigeBestimmungenDossier', sonstigeBestimmungenDossier)

# Atomic simple type: vorgang
class vorgang (text4):

    """Angaben über Tätigkeiten, die an Dokumenten des Dossiers durchgeführt wurden. Es können z.B. Angaben zu Tätigkeiten sein, die im Rahmen eines Auftragssubdossiers durchgeführt wurden.Information on activities that have been carried out on the documents in the dossier. These may include e.g. information on activities carried out as part of a mandate subdossier.Informations sur les activités qui sont effectuées avec les documents du dossier. Ce peut être, par exemple, des informations sur les activités qui sont effectuées dans le cadre d'un mandat."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'vorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 202, 2)
    _Documentation = "Angaben \xfcber T\xe4tigkeiten, die an Dokumenten des Dossiers durchgef\xfchrt wurden. Es k\xf6nnen z.B. Angaben zu T\xe4tigkeiten sein, die im Rahmen eines Auftragssubdossiers durchgef\xfchrt wurden.Information on activities that have been carried out on the documents in the dossier. These may include e.g. information on activities carried out as part of a mandate subdossier.Informations sur les activit\xe9s qui sont effectu\xe9es avec les documents du dossier. Ce peut \xeatre, par exemple, des informations sur les activit\xe9s qui sont effectu\xe9es dans le cadre d'un mandat."
vorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'vorgang', vorgang)

# Atomic simple type: bemerkungDossier
class bemerkungDossier (text4):

    """Zusätzliche Informationen, welche das Dossier oder die Datensammlung betreffen. Hier können nähere Angaben zur Sprache und zu speziellen technischen Anforderungen eingetragen werden, welche den Zugang der Daten einschränken könnten.Additional information relating to the dossier or the data collection. Further information on the language and special technical requirements that may restrict access to the data may be entered here.Informations complémentaires qui concernent le dossier ou la collection de données. Ici peuvent être reportées les précisions sur la langue et sur les exigences techniques qui peuvent limiter l'accès aux données."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bemerkungDossier')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 212, 2)
    _Documentation = "Zus\xe4tzliche Informationen, welche das Dossier oder die Datensammlung betreffen. Hier k\xf6nnen n\xe4here Angaben zur Sprache und zu speziellen technischen Anforderungen eingetragen werden, welche den Zugang der Daten einschr\xe4nken k\xf6nnten.Additional information relating to the dossier or the data collection. Further information on the language and special technical requirements that may restrict access to the data may be entered here.Informations compl\xe9mentaires qui concernent le dossier ou la collection de donn\xe9es. Ici peuvent \xeatre report\xe9es les pr\xe9cisions sur la langue et sur les exigences techniques qui peuvent limiter l'acc\xe8s aux donn\xe9es."
bemerkungDossier._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bemerkungDossier', bemerkungDossier)

# Atomic simple type: titelVorgang
class titelVorgang (text3):

    """Benennung von Tätigkeit und Gegenstand des Geschäftsvorfalles.Description of activity and object of the transaction.Dénomination de l'activité et de l'objet du processus de l'activité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'titelVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 232, 2)
    _Documentation = "Benennung von T\xe4tigkeit und Gegenstand des Gesch\xe4ftsvorfalles.Description of activity and object of the transaction.D\xe9nomination de l'activit\xe9 et de l'objet du processus de l'activit\xe9."
titelVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'titelVorgang', titelVorgang)

# Atomic simple type: arbeitsanweisungVorgang
class arbeitsanweisungVorgang (text4):

    """Arbeitsanweisung, bzw.Auftragsbeschreibung: Vorgaben und Hinweise für die Durchführung und Erledigung.Instruction, guidelines and suggestions for implementation and completion.Instruction de travail ou description du mandat: directives et remarques pour l'exécution et la liquidation."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'arbeitsanweisungVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 242, 2)
    _Documentation = "Arbeitsanweisung, bzw.Auftragsbeschreibung: Vorgaben und Hinweise f\xfcr die Durchf\xfchrung und Erledigung.Instruction, guidelines and suggestions for implementation and completion.Instruction de travail ou description du mandat: directives et remarques pour l'ex\xe9cution et la liquidation."
arbeitsanweisungVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'arbeitsanweisungVorgang', arbeitsanweisungVorgang)

# Atomic simple type: federfuehrungVorgang
class federfuehrungVorgang (text3):

    """Akteur, der für die korrekte Durchführung des Geschäftsvorfalls verantwortlich ist.Player who is responsible for the correct execution of the transaction.Acteur qui est responsable de la bonne exécution du processus de l'activité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'federfuehrungVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 252, 2)
    _Documentation = "Akteur, der f\xfcr die korrekte Durchf\xfchrung des Gesch\xe4ftsvorfalls verantwortlich ist.Player who is responsible for the correct execution of the transaction.Acteur qui est responsable de la bonne ex\xe9cution du processus de l'activit\xe9."
federfuehrungVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'federfuehrungVorgang', federfuehrungVorgang)

# Atomic simple type: verweisVorgang
class verweisVorgang (text4):

    """Referenz auf andere Ordnungssystempositionen, Dossiers oder Vorgänge, die in enger Beziehung mit dem Vorgang stehen ohne direkt mit ihm verknüpft zu sein.Reference to other classification system positions, dossier or processes that are directly linked  or in close relationship with the process.Référence à d'autres positions de système de classement, dossiers ou processus qui sont en relation étroite avec le processus sans être en ligne hiérarchique directe avec lui."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'verweisVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 262, 2)
    _Documentation = "Referenz auf andere Ordnungssystempositionen, Dossiers oder Vorg\xe4nge, die in enger Beziehung mit dem Vorgang stehen ohne direkt mit ihm verkn\xfcpft zu sein.Reference to other classification system positions, dossier or processes that are directly linked  or in close relationship with the process.R\xe9f\xe9rence \xe0 d'autres positions de syst\xe8me de classement, dossiers ou processus qui sont en relation \xe9troite avec le processus sans \xeatre en ligne hi\xe9rarchique directe avec lui."
verweisVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'verweisVorgang', verweisVorgang)

# Atomic simple type: bemerkungVorgang
class bemerkungVorgang (text4):

    """Ergänzende Information zum Vorgang.Supplementary information of the transaction.Des renseignements supplémentaires du processus de l'activité."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bemerkungVorgang')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 272, 2)
    _Documentation = "Erg\xe4nzende Information zum Vorgang.Supplementary information of the transaction.Des renseignements suppl\xe9mentaires du processus de l'activit\xe9."
bemerkungVorgang._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bemerkungVorgang', bemerkungVorgang)

# Atomic simple type: vorschreibungAktivitaet
class vorschreibungAktivitaet (text3):

    """Beschreibung der Tätigkeit, die ausgeführt werden soll (Standardanweisungen).Description of the activity to be performed (standard instructions).Description de l'activité qui doit être effectuée (Instructions standard)."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'vorschreibungAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 292, 2)
    _Documentation = "Beschreibung der T\xe4tigkeit, die ausgef\xfchrt werden soll (Standardanweisungen).Description of the activity to be performed (standard instructions).Description de l'activit\xe9 qui doit \xeatre effectu\xe9e (Instructions standard)."
vorschreibungAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'vorschreibungAktivitaet', vorschreibungAktivitaet)

# Atomic simple type: anweisungAktivitaet
class anweisungAktivitaet (text4):

    """Freitext für die Eingabe der Anweisung zu einer Aktivität.Detailed description of the activity to be performed.Description détaillée de l'activité qui doit être effectuée."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'anweisungAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 302, 2)
    _Documentation = "Freitext f\xfcr die Eingabe der Anweisung zu einer Aktivit\xe4t.Detailed description of the activity to be performed.Description d\xe9taill\xe9e de l'activit\xe9 qui doit \xeatre effectu\xe9e."
anweisungAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'anweisungAktivitaet', anweisungAktivitaet)

# Atomic simple type: bearbeiterAktivitaet
class bearbeiterAktivitaet (text3):

    """Akteur, welcher die Aktivität durchführt. Im Organigramm bzw. den Organisationsvorschriften der Verwaltungseinheit aufgeführte Rollen bzw. Personen.Player which performs the activity. In the organization or the organizational rules of the administrative unit specified roles or persons.Acteur qui exécute l'activité. Rôles ou personnes mentionnés dans l'organigramme ou les directives d'organisation de l'unité administrative."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bearbeiterAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 312, 2)
    _Documentation = "Akteur, welcher die Aktivit\xe4t durchf\xfchrt. Im Organigramm bzw. den Organisationsvorschriften der Verwaltungseinheit aufgef\xfchrte Rollen bzw. Personen.Player which performs the activity. In the organization or the organizational rules of the administrative unit specified roles or persons.Acteur qui ex\xe9cute l'activit\xe9. R\xf4les ou personnes mentionn\xe9s dans l'organigramme ou les directives d'organisation de l'unit\xe9 administrative."
bearbeiterAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bearbeiterAktivitaet', bearbeiterAktivitaet)

# Atomic simple type: verweisAktivitaet
class verweisAktivitaet (text4):

    """Referenz auf andere Ordnungssystempositionen, Dossiers, Vorgänge oder Aktivitäten, die in enger Beziehung zu der Aktivität stehen ohne direkt mit ihr verknüpft zu sein.Reference to other classification system positions, dossier or processes that are directly linked  or in close relationship with the process.Référence à d'autres positions de système de classement, dossiers ou processus qui sont en relation étroite avec le processus sans être en ligne hiérarchique directe avec lui."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'verweisAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 332, 2)
    _Documentation = "Referenz auf andere Ordnungssystempositionen, Dossiers, Vorg\xe4nge oder Aktivit\xe4ten, die in enger Beziehung zu der Aktivit\xe4t stehen ohne direkt mit ihr verkn\xfcpft zu sein.Reference to other classification system positions, dossier or processes that are directly linked  or in close relationship with the process.R\xe9f\xe9rence \xe0 d'autres positions de syst\xe8me de classement, dossiers ou processus qui sont en relation \xe9troite avec le processus sans \xeatre en ligne hi\xe9rarchique directe avec lui."
verweisAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'verweisAktivitaet', verweisAktivitaet)

# Atomic simple type: bemerkungAktivitaet
class bemerkungAktivitaet (text4):

    """Informationen, die für die Aktivität von Bedeutung sind.Information of significance for the activity.Informations importantes pour l'activité"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'bemerkungAktivitaet')
    _XSDLocation = pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/dossier.xsd', 342, 2)
    _Documentation = "Informationen, die f\xfcr die Aktivit\xe4t von Bedeutung sind.Information of significance for the activity.Informations importantes pour l'activit\xe9"
bemerkungAktivitaet._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'bemerkungAktivitaet', bemerkungAktivitaet)

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
    __ca = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ca'), 'ca', '__AbsentNamespace6_historischerZeitpunkt_ca', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 9, 6), )


    ca = property(__ca.value, __ca.set, None, None)


    # Element datum uses Python identifier datum
    __datum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'datum'), 'datum', '__AbsentNamespace6_historischerZeitpunkt_datum', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 10, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace6_historischerZeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 16, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace6_historischerZeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 17, 6), )


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
    __von = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'von'), 'von', '__AbsentNamespace6_zeitraum_von', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 69, 6), )


    von = property(__von.value, __von.set, None, None)


    # Element bis uses Python identifier bis
    __bis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'bis'), 'bis', '__AbsentNamespace6_zeitraum_bis', False, pyxb.utils.utility.Location('/Users/tom/Projects/opengever.sgdemo/src/opengever.core/opengever/disposition/ech0160/schemas/base.xsd', 70, 6), )


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

