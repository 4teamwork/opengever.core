from plone.app.layout.viewlets import content


class DocumentContentHistoryViewlet(content.ContentHistoryViewlet):
    """ Custom version of content history viewlet for documents
    """

    update = content.ContentHistoryViewlet.update
