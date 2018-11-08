from opengever.base.browser.helper import get_css_class
from opengever.base.utils import escape_html
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder
from opengever.sharing import _
from opengever.sharing.treeifier import Treeify
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.globalrequest import getRequest
from zope.i18n import translate


def node_updater(brain, node):
    node['title'] = brain.Title
    node['reference'] = brain.reference
    node['url'] = brain.getURL()
    node['css_class'] = get_css_class(brain)


class BlockedLocalRolesList(BrowserView):
    """Provide an admin overview to list dossiers and repo folders with blocked
    local roles.
    """

    index = ViewPageTemplateFile('admin_list_blocked_local_roles.pt')

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    def render_tree(self):
        context_path = '/'.join(self.context.getPhysicalPath())
        query_filter = {
            'object_provides': (
                IRepositoryFolder.__identifier__,
                IDossierMarker.__identifier__,
                ),
            'blocked_local_roles': True,
            }

        dossier_container_brains = api.content.find(
            context=self.context, **query_filter)

        if dossier_container_brains:
            title = escape_html(translate(
                _(
                    u'label_blocked_local_roles',
                    default=u'Protected Objects',
                    ),
                context=getRequest(),
                ))

            title_element = u''.join((u'<h1>', title, u'</h1>', ))

            tree = Treeify(
                dossier_container_brains,
                context_path, node_updater,
                )

            # XXX - Preserving the reference number tree order.
            # Sorting here was easier than figuring out the treeifying.
            iterable_children = sorted(
                tree(self.context).get('children', ()),
                key=lambda child: child.get('title', ''),
                )

            rendered_tree = self._build_html_tree(iterable_children)

            garnished_tree = ''.join((
                title_element,
                rendered_tree,
                ))

            return garnished_tree

        title = escape_html(translate(
            _(
                u'label_no_blocked_local_roles',
                default=u'No protected objects were found within this scope.',
                ),
            context=getRequest(),
            ))

        title_element = u''.join((u'<h1>', title, u'</h1>', ))

        return title_element

    def _build_html_tree(self, children=(), level=1):
        output = u''

        for node in children:
            output = u''.join((
                output,
                u'<li class="treeItem visualNoMarker">\n',
                ))

            title = escape_html(node.get('title'))
            reference = escape_html(node.get('reference'))
            url = escape_html(node.get('url'))
            css_class = node.get("css_class")
            sub_children = node.get('children')

            if title:
                if url and title:
                    anchor = (
                        u'#blocked-local-roles' if sub_children
                        else u'#sharing'
                        )
                    target_url = u''.join((url.decode('UTF-8'), anchor, ))

                    output = u''.join((
                        output,
                        u'<a class="{} blocked-local-roles-link" href="{}">{} - {}</a>'
                        .format(
                            css_class,
                            target_url,
                            title.decode('UTF-8'),
                            reference,
                            ),
                        ))
                else:
                    output = u''.join((
                        output,
                        u'<span class="{} blocked-local-roles-link">{} - {}</span>'
                        .format(
                            css_class,
                            title.decode('UTF-8'),
                            reference,
                            ),
                        ))

            if sub_children:
                output = u''.join((
                    output,
                    u'<ul class="level{}">\n{}\n</ul>\n'.format(
                        str(level),
                        self._build_html_tree(sub_children, level + 1),
                        ),
                    ))

            output.join((output, u'</li>\n', ))

        return output
