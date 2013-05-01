import logging
import sqlalchemy
import transaction
from sqlalchemy.exc import OperationalError
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


class ActiveUsersSection(object):
    """This section first sets all users in the SQL DB to inactive.
    It then iterates over all the items from the previous section
    (LDAP users) and sets all the users that are still contained
    in the LDAP to active.
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
        self.table = Table(tablename, meta, autoload=True,
                           autoload_with=self.connection.engine)

    def __iter__(self):
        # First, set all the users in the SQL DB to inactive
        set_all_inactive = update(self.table)
        self.connection.execute(set_all_inactive, {'active': '0'})
        transaction.commit()

        for item in self.previous:
            try:
                # Then set the ones still contained in the LDAP to active
                u = update(
                    self.table,
                    self.table.c.get('userid') == item.get('userid'))

                self.connection.execute(u, {'active': '1'})
                yield item

            except OperationalError, e:
                transaction.abort()
                self.logger.warn("SQL operational error: %s" % e)
            except:
                transaction.abort()
                raise

        transaction.commit()
