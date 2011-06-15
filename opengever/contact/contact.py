from five import grok

from zope import schema
from collective import dexteritytextindexer
from plone.dexterity.content import Item
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile.field import NamedImage


from opengever.contact import _

from plone.directives import dexterity


class IContact(form.Schema):
    """ A contact
    """
    form.fieldset(
        u'personal',
        label = _(u'personal', default=u'Personal Stuff'),
        fields = [
            u'salutation',
            u'academic_title',
            u'firstname',
            u'lastname',
            u'description',
            u'picture',
            u'company',
            u'department',
            u'function',
        ])

    form.fieldset(
        u'internet',
        label = _(u'internet', default=u'Internet'),
        fields= [
            u'email',
            u'email2',
            u'url',
        ])

    form.fieldset(
        u'telefon',
        label= _(u'telefon', default=u"Telefon"),
        fields= [
            u'phone_office',
            u'phone_fax',
            u'phone_mobile',
            u'phone_home',
        ])

    form.fieldset(
        u'address',
        label= _(u'address', default=u'Address'),
        fields= [
            u'address1',
            u'address2',
            u'zip_code',
            u'city',
            u'country',
        ])

    salutation = schema.TextLine(
        title = _(u'label_salutation', default=u'Salutation'),
        description = _(u'help_salutation', default=u''),
        required = False,
        )

    academic_title = schema.TextLine(
        title = _(u'label_academic_title', default=u'Academic title'),
        description = _(u'help_academic_title', default=u''),
        required = False,
        )

    dexteritytextindexer.searchable('lastname')
    lastname = schema.TextLine(
        title = _(u'label_lastname', default=u'Lastname'),
        description = _(u'help_lastname', default=u''),
        required = True,
        )

    dexteritytextindexer.searchable('firstname')
    firstname = schema.TextLine(
        title = _(u'label_firstname', default=u'Firstname'),
        description = _(u'help_firstname', default=u''),
        required = True,
        )

    company = schema.TextLine(
        title = _(u'label_company', default=u"Company"),
        description = _(u'help_company', default=u''),
        required = False,
        )

    department = schema.TextLine(
        title = _(u'label_department', default=u'Department'),
        description = _(u'help_department', default=u''),
        required = False,
        )

    function = schema.TextLine(
        title = _(u'lable_function', default=u'Function'),
        description = _(u'help_function', default=u''),
        required = False,
        )

    email = schema.TextLine(
        title = _(u'label_email', default=u'email'),
        description = _(u'help_email', default=u''),
        required = False,
        )

    email2 = schema.TextLine(
        title = _(u'label_email2', default=u'Email 2'),
        description = _('help_email2', default=u''),
        required = False,
        )

    url = schema.URI(
        title = _(u'label_url', default=u'Url'),
        description = _(u'help_url', default=u''),
        required = False,
        )

    phone_office = schema.TextLine(
        title = _(u'label_phone_office', default=u'Phone office'),
        description = _(u'help_phone_office', default=u''),
        required = False,
        )

    phone_fax = schema.TextLine(
        title = _(u'label_phone_fax', default=u'Fax'),
        description = _(u'help_phone_fax', default=u''),
        required = False,
        )

    phone_mobile = schema.TextLine(
        title = _(u'label_phone_mobile', default=u'Mobile'),
        description = _(u'help_phone_mobile', default=u''),
        required = False,
        )

    phone_home = schema.TextLine(
        title = _(u'label_phone_home', default=u'Phone home'),
        description = _(u'help_phone_home', default=u''),
        required = False,
        )

    picture = NamedImage(
        title=_(u'label_picture', default='Picture'),
        required=False,
        )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description = _(u'help_description', default=u''),
        required=False,
        )

    address1 = schema.TextLine(
        title = _(u'label_address1', default=u'Address 1'),
        description = _(u'help_address1', default=u''),
        required = False,
        )

    address2 = schema.TextLine(
        title = _(u'label_address2', default=u'Address 2'),
        description = _(u'help_address2', default=u''),
        required = False,
        )

    zip_code = schema.TextLine(
        title = _(u'label_zip', default=u'ZIP'),
        description = _(u'help_zip', default=u''),
        required = False,
        )

    city = schema.TextLine(
        title = _(u'label_city', default=u'City'),
        description = _(u'help_city', default=u''),
        required = False,
        )

    country = schema.TextLine(
        title = _(u'label_country', default=u'Country'),
        description = _(u'help_country', default=u''),
        required = False,
        )


class Contact(Item):

    def contactid(self):
        return 'contact:%s' % self.id

    @property
    def title(self):
        title = '%s %s' % (
            self.lastname,
            self.firstname,
            )
        if len(title.strip())==0:
            title = _(u'Contact')
        return title

    def setTitle(self, title):
        """ Dummy action (is called while creating object)
        """
        pass


@indexer(IContact)
def contactid(obj):
    return obj.contactid
grok.global_adapter(contactid, name='contactid')


@indexer(IContact)
def phone_office(obj):
    return obj.phone_office
grok.global_adapter(phone_office, name='phone_office')


@indexer(IContact)
def firstname(obj):
    return obj.firstname
grok.global_adapter(firstname, name='firstname')


@indexer(IContact)
def lastname(obj):
    return obj.lastname
grok.global_adapter(lastname, name='lastname')


class View(dexterity.DisplayForm):
    grok.context(IContact)
    grok.require('zope2.View')
    grok.name('contact_view')
