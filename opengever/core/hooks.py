from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
import logging
import opengever.activity.hooks
import opengever.base.hooks
import opengever.contact.hooks
import opengever.document.hooks
import opengever.dossier.hooks
import opengever.inbox.hooks
import opengever.ogds.base.hooks
import opengever.private.hooks
import opengever.quota.hooks
import opengever.repository.hooks
import opengever.tabbedview.hooks
import opengever.task.hooks
import opengever.trash.hooks
import opengever.workspace.hooks
import opengever.workspaceclient.hooks
import re


LOG = logging.getLogger('opengever.core.hooks')

# Forbidden profiles are never allowed to be installed.
FORBIDDEN_PROFILES = (
    'opengever.ogds.base:default',
    'opengever.globalindex:default',
    'opengever.base:default',
    'opengever.document:default',
    'opengever.mail:default',
    'opengever.dossier:default',
    'opengever.repository:default',
    'opengever.journal:default',
    'opengever.task:default',
    'opengever.tabbedview:default',
    'opengever.trash:default',
    'opengever.inbox:default',
    'opengever.tasktemplates:default',
    'opengever.portlets.tree:default',
    'opengever.contact:default',
    'opengever.advancedsearch:default',
    'opengever.sharing:default',
    'opengever.latex:default',
    'opengever.meeting:default',
    'opengever.activity:default',
    'opengever.bumblebee:default',
    'opengever.officeatwork:default',
    'opengever.officeconnector:default',
    'opengever.private:default',
    'opengever.disposition:default',
    'opengever.policy.base:default')


def avoid_profile_reinstallation(event):
    profile = re.sub('^profile-', '', event.profile_id)
    assert profile not in FORBIDDEN_PROFILES, \
        'It is not allowed to install the profile {!r}.'.format(profile)

    request = getSite().REQUEST
    annotations = IAnnotations(request)
    key = 'opengever.core:avoid_profile_reinstallation'
    if key not in annotations:
        annotations[key] = []

    if should_prevent_duplicate_installation(profile):
        assert profile not in annotations[key], \
            'Profile {!r} should not be installed twice.'.format(profile)
    elif profile in annotations[key]:
        LOG.warning('%r installed twice', profile)

    annotations[key].append(profile)


def should_prevent_duplicate_installation(profile):
    return (
        profile.startswith('opengever.')
        or profile.startswith('ftw.')
        or profile.startswith('plonetheme.teamraum')
    )


def installed(site):
    trigger_subpackage_hooks(site)
    enable_secure_flag_for_cookies(site)
    remove_unused_catalog_indexes(site)
    remove_unused_catalog_metadata(site)


def trigger_subpackage_hooks(site):
    # The hooks are ordered by the dependency order of the subpackage
    # profiles before the profile merge.
    opengever.ogds.base.hooks.default_installed(site)
    opengever.base.hooks.installed(site)
    opengever.document.hooks.installed(site)
    opengever.dossier.hooks.installed(site)
    opengever.task.hooks.installed(site)
    opengever.tabbedview.hooks.installed(site)
    opengever.trash.hooks.installed(site)
    opengever.inbox.hooks.installed(site)
    opengever.contact.hooks.installed(site)
    opengever.activity.hooks.insert_notification_defaults(site)
    opengever.private.hooks.configure_members_area(site)
    opengever.quota.hooks.policy_installed(site)
    # Added after the profile merge
    opengever.repository.hooks.installed(site)
    opengever.workspace.hooks.installed(site)
    opengever.workspaceclient.hooks.installed(site)


def enable_secure_flag_for_cookies(context):
    session_plugin = context.acl_users.session
    session_plugin.secure = True


def remove_unused_catalog_indexes(site):
    indexes_to_remove = [
        'commentators',
        'Date',
        'Description',
        'effective',
        'effectiveRange',
        'expires',
        'getRawRelatedItems',
        'in_reply_to',
        'is_default_page',
        'meta_type',
        'SearchableText',
        'total_comments',
    ]
    catalog = api.portal.get_tool('portal_catalog')
    for index in indexes_to_remove:
        if index in catalog._catalog.indexes:
            catalog._catalog.delIndex(index)


def remove_unused_catalog_metadata(site):
    columns_to_remove = [
        'author_name',
        'commentators',
        'CreationDate',
        'Date',
        'effective',
        'EffectiveDate',
        'ExpirationDate',
        'expires',
        'getObjSize',
        'getRemoteUrl',
        'last_comment_date',
        'location',
        'meta_type',
        'ModificationDate',
        'total_comments',
    ]
    catalog = api.portal.get_tool('portal_catalog')
    for column in columns_to_remove:
        if column in catalog._catalog.schema:
            catalog._catalog.delColumn(column)
