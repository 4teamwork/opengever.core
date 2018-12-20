from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.oguid import Oguid
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class SubmittedDocument(Base):
    """Represents a document that was submitted with a proposal.

    Links document in a proposal's dossier to the submitted version in a
    submitted proposal.

    """
    __tablename__ = 'submitteddocuments'
    __table_args__ = (
        UniqueConstraint('admin_unit_id', 'int_id', 'proposal_id',
                         name='ix_s_docs_unique_src'),
        UniqueConstraint('submitted_admin_unit_id', 'submitted_int_id',
                         name='ix_s_docs_unique_dst'),
        {})

    document_id = Column("id", Integer, Sequence("submitteddocument_id_seq"),
                         primary_key=True)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=False)
    proposal = relationship("Proposal", backref='submitted_documents')
    submitted_version = Column(Integer, nullable=False)

    submitted_admin_unit_id = Column(String(UNIT_ID_LENGTH))
    submitted_int_id = Column(Integer)
    submitted_oguid = composite(
        Oguid, submitted_admin_unit_id, submitted_int_id)
    submitted_physical_path = Column(String(256))

    def __repr__(self):
        return "<SubmittedDocument {}@{}>".format(
            self.int_id, self.admin_unit_id)

    def is_up_to_date(self, document):
        assert Oguid.for_object(document) == self.oguid, 'invalid document'

        return self.submitted_version == document.get_current_version_id(
            missing_as_zero=True)

    def resolve_submitted(self):
        return self.submitted_oguid.resolve_object()

    def resolve_source(self):
        """Resolve the source document."""

        return self.oguid.resolve_object()
