from opengever.base.model import Base
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import create_session
from opengever.base.model import EMAIL_LENGTH
from opengever.base.utils import to_safe_html
from opengever.contact.docprops import MailAddressDocPropertyProvider
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class MailAddress(Base):
    __tablename__ = 'mail_addresses'

    mailaddress_id = Column('id', Integer, Sequence('mail_adresses_id_seq'),
                            primary_key=True)
    contact_id = Column('contact_id', Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="mail_addresses")
    label = Column(String(CONTENT_TITLE_LENGTH))
    address = Column(String(EMAIL_LENGTH), nullable=False)

    def serialize(self):
        return {
            'id': self.mailaddress_id,
            'contact_id': self.contact_id,
            'label': self.label,
            'address': self.address,
            'delete_url': self.get_delete_url(),
            'update_url': self.get_update_url(),
            }

    def get_delete_url(self):
        return self.contact.get_url(
            'mails/{}/delete'.format(self.mailaddress_id))

    def get_update_url(self):
        return self.contact.get_url(
            'mails/{}/update'.format(self.mailaddress_id))

    def delete(self):
        session = create_session()
        session.delete(self)

    def update(self, **kwargs):
        self._set_field('label', kwargs.get('label', ''))
        self._set_field('address', kwargs.get('address', ''))

    def _set_field(self, name, value):
        if name is None:
            return

        setattr(self, name, to_safe_html(value))

    def get_doc_property_provider(self):
        return MailAddressDocPropertyProvider(self)
