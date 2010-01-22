from StringIO import StringIO
import logging 
#from zope.component import getUtility, getAdapter, getMultiAdapter

class SetupVarious(object):

    def __call__(self, setup):
        logger = logging.getLogger('opengever.examplecontent:journal')
        self.setup = setup
        out = StringIO()
        site = setup.getSite()
        self.addJournal(site, out)
        logger.info("created journal")

    def addJournal(self, p, out):
        
        newid = p.invokeFactory(id='journal', title='Journal', type_name='Topic')
        journal = p[newid]
        
        sort_on = 'modified'
        reversed = True
        journal.setSortCriterion(sort_on, reversed)
        criteria = journal.listCriteria()
        
        MARKER=[]

        DATA = {}

        for criterion in criteria:
            id  = criterion.getId()
            schematas = criterion.Schemata()
            fields = [field for field in schematas['default'].fields()
                            if field.mode != 'r' ]

            for field in fields:
                fid = '%s_%s' % (id, field.getName())
                rval = DATA.get(fid, MARKER)
                accessor = field.getAccessor(criterion)
                if rval is not MARKER and accessor() != rval:
                    mutator = field.getMutator(criterion)
                    mutator(rval)
