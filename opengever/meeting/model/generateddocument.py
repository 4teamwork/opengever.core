from opengever.base.model import Base
from opengever.base.oguid import Oguid
from opengever.meeting.model.query import GeneratedDocumentQuery
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.schema import Sequence


class GeneratedDocument(Base):
    """Base class to track a document that was generated at some point.

    Keeps a reference to the created document by storing it's oguid.

    """
    query_cls = GeneratedDocumentQuery

    __tablename__ = 'generateddocuments'
    __table_args__ = (
        UniqueConstraint('admin_unit_id', 'int_id',
                         name='ix_generated_document_unique'),
        {})

    document_id = Column("id", Integer, Sequence("generateddocument_id_seq"),
                         primary_key=True)
    admin_unit_id = Column(String(30), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    generated_version = Column(Integer, nullable=False)

    generated_document_type = Column(String(100), nullable=False)
    __mapper_args__ = {'polymorphic_on': generated_document_type}

    def __repr__(self):
        return "<GeneratedDocument {}@{}>".format(
            self.int_id, self.admin_unit_id)

    def is_up_to_date(self, document):
        assert Oguid.for_object(document) == self.oguid, 'invalid document'

        return self.generated_version == document.get_current_version()

    def resolve_document(self):
        return self.oguid.resolve_object()


class GeneratedPreProtocol(GeneratedDocument):

    __mapper_args__ = {'polymorphic_identity': 'generated_pre_protocol'}


class GeneratedProtocol(GeneratedDocument):

    __mapper_args__ = {'polymorphic_identity': 'generated_protocol'}
