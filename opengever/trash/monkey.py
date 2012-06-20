def search_patch(scope, original, replacement):
    orimethod = getattr(scope, original)

    def newSearchResult(self, REQUEST=None, **kw):
        kw = kw.copy()
        if 'trashed' not in kw.keys():
            kw['trashed'] = [False, None]
        return orimethod(self, REQUEST, **kw)
    setattr(scope, original, newSearchResult)
    setattr(scope, '__call__', newSearchResult)
    return


def dummy_method(self, REQUEST=None, **kw):
    pass
