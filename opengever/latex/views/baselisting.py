from Products.CMFCore.utils import getToolByName
from opengever.globalindex.interfaces import ITaskQuery
from opengever.latex.layouts.zug_default import ZugDefaultLayout
from plonegov.pdflatex.browser.aspdf import AsPDFView
from zope.component import getUtility


class BasePDFListing(AsPDFView):
    """Basic view for creating a pdf of object selected in a tabbed view.
    """

    # Latex template file
    template = None

    def __call__(self, *args, **kwargs):
        if 'default_book_settings' not in kwargs:
            kwargs['default_book_settings'] = False
        if 'pre_compiler' not in kwargs:
            kwargs['pre_compiler'] = self.get_layout()
        return AsPDFView.__call__(self, *args, **kwargs)

    def get_layout(self):
        """Returns the layout to use.
        """
        return ZugDefaultLayout(show_contact=False)

    def _generate_latex(self, *a, **kw):
        """We do not render the context but a catalog query.
        """
        # generate body late
        latex_body = self.render()
        self.latex_properties['latex_body'] = latex_body
        # generate document
        generator = self.latex_generator(self.context)
        latex_doc = generator.generate(**self.latex_properties)
        return latex_doc

    def render(self):
        """Renders the template
        """
        return self.template()

    def get_selected_data(self):
        """Returns either a set of brains or a set of SQLAlchemy objects -
        depending on the (tabbed-) view where the tasks were selected.
        If there is a "path:list" in the request, we use the catalog and
        if there is a "task_id:list", we use SQLAlchemy.
        """

        paths = self.request.get('paths', None)
        ids = self.request.get('task_ids', [])

        if paths:
            catalog = getToolByName(self.context, 'portal_catalog')

            for path in self.request.get('paths', []):
                brains = catalog({'path': {'query': path,
                                       'depth': 0}})
                assert len(brains) == 1, "Could not find task at %s" % path
                yield brains[0]

        elif ids:
            query = getUtility(ITaskQuery)

            # we need to sort the result by our ids list, because the
            # sql query result is not sorted...
            # create a mapping:
            mapping = {}
            for task in query.get_tasks(ids):
                mapping[str(task.task_id)] = task

            # get the task from the mapping
            for id in ids:
                task = mapping.get(str(id))
                if task:
                    yield task

        else:
            # empty generator
            pass


    def _prepare_table_row(self, *cells):
        """Converts every cell in `cells` into LaTeX and merges them
        to a LaTeX row.
        """

        return '%s%s' % (' & '.join([self.convert(cell) for cell in cells]),
                         '\\\\ \\hline\n')
