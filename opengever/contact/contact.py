from collective import dexteritytextindexer
from opengever.base.model import EMAIL_LENGTH
from opengever.base.model import FIRSTNAME_LENGTH
from opengever.base.model import LASTNAME_LENGTH
from opengever.contact import _
from plone.dexterity.content import Item
from plone.indexer import indexer
from plone.namedfile.field import NamedImage
from plone.supermodel import model
from zope import schema


class IContact(model.Schema):
    """ A contact
    """
    model.fieldset(
        u'personal',
        label=_(u'personal', default=u'Personal Stuff'),
        fields=[
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

    model.fieldset(
        u'internet',
        label=_(u'internet', default=u'Internet'),
        fields=[
            u'email',
            u'email2',
            u'url',
        ])

    model.fieldset(
        u'telefon',
        label=_(u'telefon', default=u"Telefon"),
        fields=[
            u'phone_office',
            u'phone_fax',
            u'phone_mobile',
            u'phone_home',
        ])

    model.fieldset(
        u'address',
        label=_(u'address', default=u'Address'),
        fields=[
            u'address1',
            u'address2',
            u'zip_code',
            u'city',
            u'country',
        ])

    salutation = schema.TextLine(
        title=_(u'label_salutation', default=u'Salutation'),
        required=False,
        )

    academic_title = schema.TextLine(
        title=_(u'label_academic_title', default=u'Academic title'),
        required=False,
        )

    dexteritytextindexer.searchable('lastname')
    lastname = schema.TextLine(
        title=_(u'label_lastname', default=u'Lastname'),
        required=True,
        max_length=LASTNAME_LENGTH,
        )

    dexteritytextindexer.searchable('firstname')
    firstname = schema.TextLine(
        title=_(u'label_firstname', default=u'Firstname'),
        required=True,
        max_length=FIRSTNAME_LENGTH,
        )

    company = schema.TextLine(
        title=_(u'label_company', default=u"Company"),
        required=False,
        )

    department = schema.TextLine(
        title=_(u'label_department', default=u'Department'),
        required=False,
        )

    function = schema.TextLine(
        title=_(u'lable_function', default=u'Function'),
        required=False,
        )

    email = schema.TextLine(
        title=_(u'label_email', default=u'email'),
        required=False,
        max_length=EMAIL_LENGTH,
        )

    email2 = schema.TextLine(
        title=_(u'label_email2', default=u'Email 2'),
        required=False,
        max_length=EMAIL_LENGTH,
        )

    url = schema.URI(
        title=_(u'label_url', default=u'Url'),
        required=False,
        )

    phone_office = schema.TextLine(
        title=_(u'label_phone_office', default=u'Phone office'),
        required=False,
        )

    phone_fax = schema.TextLine(
        title=_(u'label_phone_fax', default=u'Fax'),
        required=False,
        )

    phone_mobile = schema.TextLine(
        title=_(u'label_phone_mobile', default=u'Mobile'),
        required=False,
        )

    phone_home = schema.TextLine(
        title=_(u'label_phone_home', default=u'Phone home'),
        required=False,
        )

    picture = NamedImage(
        title=_(u'label_picture', default='Picture'),
        required=False,
        )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False,
        missing_value=u'',
        )

    address1 = schema.TextLine(
        title=_(u'label_address1', default=u'Address 1'),
        required=False,
        )

    address2 = schema.TextLine(
        title=_(u'label_address2', default=u'Address 2'),
        required=False,
        )

    zip_code = schema.TextLine(
        title=_(u'label_zip', default=u'ZIP'),
        required=False,
        )

    city = schema.TextLine(
        title=_(u'label_city', default=u'City'),
        required=False,
        )

    country = schema.TextLine(
        title=_(u'label_country', default=u'Country'),
        required=False,
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
        if len(title.strip()) == 0:
            title = _(u'Contact')
        return title

    def setTitle(self, title):
        """ Dummy action (is called while creating object)
        """
        pass


@indexer(IContact)
def contactid(obj):
    return obj.contactid


@indexer(IContact)
def phone_office(obj):
    return obj.phone_office


@indexer(IContact)
def firstname(obj):
    return obj.firstname


@indexer(IContact)
def lastname(obj):
    return obj.lastname
