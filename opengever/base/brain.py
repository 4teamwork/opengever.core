from opengever.base.utils import get_preferred_language_code


def useBrains(self, brains):
    """ Sets up the Catalog to return an object (ala ZTables) that
    is created on the fly from the tuple stored in the self.data
    Btree.
    """

    self._old_useBrains(brains)

    class mybrains(self._v_result_class):

        @property
        def Title(self):
            code = get_preferred_language_code()
            title = getattr(self, 'title_%s' % code, None)
            if not title:
                title = getattr(self, 'title_de', None)

            if not title:
                title = super(mybrains, self).Title

            return title

    self._v_result_class = mybrains
