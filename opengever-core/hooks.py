def print_imported_gs_profile(event):
    print 'IMPORTING', event.profile_id


def installed(site):
    trigger_subpackage_hooks(site)


def trigger_subpackage_hooks(site):
    # The hooks are ordered by the dependency order of the subpackage
    # profiles before the profile merge.
