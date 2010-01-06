

class SetupVarious(object):

    def __call__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile

