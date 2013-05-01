from plone.testing import Layer


class MemoryDBLayer(Layer):
    """A Layer which only set up a test sqlite db in to the memory
    """

    def testSetUp(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from opengever.globalindex.model import Base
        from opengever.globalindex.model.task import Task
        #make pyflakes happy
        Task
        engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        # create tables
        Base.metadata.create_all(session.bind)

        self.session = session

    def testTearDown(test):

        #test.globs['session'].remove()
        pass


MEMORY_DB_LAYER = MemoryDBLayer()
