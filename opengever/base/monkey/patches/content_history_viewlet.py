from opengever.base.monkey.patching import MonkeyPatch


class PatchFullHistory(MonkeyPatch):

    def __call__(self):

        def fullHistory(viewlet):
            history = original_fullHistory(viewlet)
            if history is None:
                history = []
            return history

        from plone.app.layout.viewlets.content import ContentHistoryViewlet

        locals()['__patch_refs__'] = False
        original_fullHistory = ContentHistoryViewlet.fullHistory
        self.patch_refs(ContentHistoryViewlet, 'fullHistory', fullHistory)
