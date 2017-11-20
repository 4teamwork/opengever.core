def reindex_blocked_local_roles(repofolder, event):
    """Reindex blocked_local_roles upon the acquisition blockedness changing."""
    repofolder.reindexObject(idxs=['blocked_local_roles'])
