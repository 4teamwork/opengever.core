# -*- coding: utf-8 -*-
from opengever.base.interfaces import IFavoritesSettings
from opengever.base.interfaces import ISearchSettings
from plone import api
from plone.i18n.locales import languages
from zope.i18nmessageid import MessageFactory
import csv

_ = MessageFactory('opengever.base')

from opengever.base import monkey  # noqa


VERSION = 'GEVER Version %(version)s'


def is_favorites_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IFavoritesSettings)


def is_solr_feature_enabled():
    return api.portal.get_registry_record(
        'use_solr', interface=ISearchSettings)


class OpenGeverCSVDialect(csv.excel):
    """A CSV dialect based on the standard Excel dialect but with support for
    escaped characters (double quotes in particular).
    """
    escapechar = '\\'


csv.register_dialect(u'OpenGeverCSV', OpenGeverCSVDialect)


# configure visible language codes. Unfortunately this cannot be done in a .po
# file.
languages._combinedlanguagelist['de-ch']['native'] = u'Deutsch'
languages._combinedlanguagelist['fr-ch']['native'] = u'Français'
