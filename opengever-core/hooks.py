from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
import logging
import re


LOG = logging.getLogger('opengever.core.hooks')

# Forbidden profiles are never allowed to be installed.
FORBIDDEN_PROFILES = ()


def awoid_profile_reinstallation(event):
    profile = re.sub('^profile-', '', event.profile_id)
    assert profile not in FORBIDDEN_PROFILES, \
        'It is not allowed to install the profile {!r}.'.format(profile)

    request = getSite().REQUEST
    annotations = IAnnotations(request)
    key = 'opengever.core:awoid_profile_reinstallation'
    if key not in annotations:
        annotations[key] = []

    if profile.startswith('opengever.') or profile.startswith('ftw.'):
        assert profile not in annotations[key], \
            'Profile {!r} should not be installed twice.'.format(profile)
    elif profile in annotations[key]:
        LOG.warning('{!r} installed twice'.format(profile))

    annotations[key].append(profile)


def installed(site):
    trigger_subpackage_hooks(site)


def trigger_subpackage_hooks(site):
    # The hooks are ordered by the dependency order of the subpackage
    # profiles before the profile merge.
