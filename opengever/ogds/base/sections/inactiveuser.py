import logging
import sqlalchemy
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.sql.expression import update
from sqlalchemy import Table
from sqlalchemy.schema import MetaData
from zope.interface import classProvides, implements
from zope.annotation import IAnnotations
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from z3c.saconfig import named_scoped_session

Session = named_scoped_session("opengever")

SQLSOURCE_KEY = 'transmogrify.sqlinserter.sqlinsertersection'

class InactiveUserSection(object):
    """The Section which set all user which doesn't exist in the LDAP to inactiv.
    for that Reason it check the import_stamp
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.context = transmogrifier.context

        # Get the dsn from our named session
        dsn = str(Session.bind.url)
        # Allow for connection reuse along a pipeline
        #dsn = options['dsn']
        conns = IAnnotations(transmogrifier).setdefault(SQLSOURCE_KEY, {})
        if dsn in conns:
            self.connection = conns[dsn]
        else:
            engine = sqlalchemy.create_engine(dsn)
            conns[dsn] = self.connection = engine.connect()

        meta = MetaData()
        tablename = options['table']
        self.table = Table(tablename, meta, autoload=True, autoload_with=self.connection.engine)
        self.stamp_key = options.get('stamp_key', None)

    def __iter__(self):
        for item in self.previous:
            yield item

        trans = self.connection.begin()
        try:
            u = update(self.table, self.table.c.get(self.stamp_key) !=item.get(self.stamp_key))
            self.connection.execute(u, {'active':'0'})
            trans.commit()
        except OperationalError, e:
            trans.rollback()
            self.logger.warn("SQL operational error: %s" % e)
        except:
            trans.rollback()
            raise
