from ftw.table.interfaces import ITableGenerator
from opengever.base import _
from opengever.base.utils import escape_html
from opengever.base.utils import NullObject
from plone.app.z3cform.views import RenderWidget
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form import util
from z3c.form.browser import widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ISequenceWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import SequenceWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ITitledTokenizedTerm
import json


class GeverRenderWidget(RenderWidget):
    """Renders the widget with the possiblity to add a dynamic description.

    Add a new property to the widget in your form to display a dynamic
    description instead the default field description:

    widget.dynamic_description = u"My dynamic description"


    Motivation:
    The default behavior is, that the field description will be displayed
    if it's available.

    If you want to change the description for a specific widget only for
    a specific request there was no possiblity to do that. Changing the
    fields description is not an option because it is persistent.
    """
    index = ViewPageTemplateFile('templates/widget.pt')

    def get_description(self):
        if hasattr(self.context, 'dynamic_description') and self.context.dynamic_description:
            return escape_html(self.context.dynamic_description)
        return self.context.field.description


class ITableRadioWidget(ISequenceWidget):
    """Table based radio-button widget."""


class TableRadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Render a choice (radio-buttons) in a table with ftw.table.

    The TableChoice field can be configured with a tuple of additional
    columns. If custom columns are configured render a table with the
    radio-button column as first column followed by the custom columns. If no
    such columns are defined render the default column displaying the term's
    title.

    """
    implementsOnly(ITableRadioWidget)

    klass = u'radio-widget'
    css = u'radio'

    empty_message = _("msg_no_items_available", default=u"No items available")

    def show_filter(self):
        return self.field.show_filter

    def is_checked(self, term):
        return term.token in self.value

    def has_items(self):
        return len(self.terms) > 0

    def render_table(self):
        """Render the table that contains the radio-button sequence.

        Always renders a radio-button column as first column.
        If the field defines custom columns render these, if it does not
        render a column with the term's title.

        While rendering the table we pass only the token-values (i.e. the
        objects) to the ITableGenerator. This improves compatibility with
        already existing helpers that expect objects and not vocabulary-terms
        and with the ITableGenerator itself since it can perform attribe
        lookups based on the column name.

        """
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        radio_column = ({
            'transform': self.render_token_radiobutton,
            'sortable': False
        },)
        default_title_colum = ({
            'column_title': _(u'label_title', default=u'Title'),
            'transform': self.render_default_title,
        },)
        columns = radio_column + (self.field.columns or default_title_colum)
        rows = [term.value for term in self.terms]
        if not self.field.required:
            rows = [NullObject()] + rows
        return generator.generate(rows, columns)

    def ajax_render(self):
        """Render and return the widget HTML so that it can be replaced
        in an existing browser page with an AJAX call.
        """
        self.form.update()
        self.update()
        self.terms = None
        self.updateTerms()
        return self()

    def render_token_radiobutton(self, item, value):
        """Render the radio-button input element for an item."""
        if isinstance(item, NullObject):
            # XXX - the checkedness persistency does not work as this is not a real value being passed in
            return (
                u'<input id="{id}" name="{name}" value="{value}" title="{title}" type="radio" "{checked}" />'
                .format(
                    id=u'-'.join((self.id, u'empty-marker')),
                    name=self.name,
                    value=u'--NOVALUE--',
                    checked=u'checked="checked"' if u'--NOVALUE--' in self.value else u'',
                    title=_(u'label_none', default=u'None'),
                    )
                )

        term = self.terms.getTerm(item)

        is_checked = self.is_checked(term)
        item_id = '%s-%s' % (self.id, term.token)

        return u'<input id="{id}" name="{name}" value="{value}"'\
            'title="{title}" type="radio" {checked} />'.format(
                id=item_id,
                name=escape_html(self.name),
                value=term.token,
                checked='checked="checked"' if is_checked else '',
                title=escape_html(self.render_default_title(item, value)),
            )

    def render_default_title(self, item, value):
        """Render the default title colum with the term's title."""
        if isinstance(item, NullObject):
            return _(u'label_none', default=u'None')

        term = self.terms.getTerm(item)

        if ITitledTokenizedTerm.providedBy(term):
            label = translate(term.title, context=self.request,
                              default=term.title)
        else:
            label = util.toUnicode(term.value)
        return label

    def get_vocabulary_depends_on(self):
        if not self.field.vocabulary_depends_on:
            return None
        return json.dumps(self.field.vocabulary_depends_on)

    def update(self):
        """See z3c.form.interfaces.IWidget."""

        super(TableRadioWidget, self).update()
        widget.addFieldClass(self)


@adapter(ITableRadioWidget, IFormLayer)
@implementer(IFieldWidget)
def TableRadioFieldWidget(field, request):
    """IFieldWidget factory for TableRadioWidget."""

    return FieldWidget(field, TableRadioWidget(request))


@implementer(IFieldWidget)
@adapter(ISequence, ITextLine, IDefaultBrowserLayer)
def SequenceTextLinesFieldWidget(field, value_type, request):
    """ There is no default sequence widget for TextLine types
    """
    return TextLinesFieldWidget(field, request)
