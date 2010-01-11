import csv

class SetupVarious(object):
    
    def __call__(self, setup):
        self.fileencoding = 'utf8'
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.create_users()

    def create_users(self):
        password = 'demo09'
        file = self.openDataFile('users.csv')
        users = self._get_objects_data(file)
        regtool = self.portal.portal_registration
        acl_users = self.portal.acl_users
        groupstool = self.portal.portal_groups
        for user in users:
            if acl_users.getUserById(user['userid']):
                continue
            member = regtool.addMember(
                user['userid'],
                password,
                ('Member',),
                None,
                properties={
                    'username' : user['userid'],
                    'email' : user['email'],
                    }
                )
            member.setMemberProperties({
                    'fullname' : '%s %s' % (
                        user['firstname'],
                        user['lastname'],
                        )
                    })
            # groups are comma-seperated
            for gid in user['groups'].split(','):
                if not groupstool.getGroupById(gid):
                    groupstool.addGroup(gid)
                    print '** created group', gid
                groupstool.getGroupById(gid).addMember(user['userid'])
            print '** created user', user['userid']

    def _get_objects_data(self, csv_stream):
        pos = csv_stream.tell()
        dialect = csv.Sniffer().sniff(csv_stream.read(1024))
        csv_stream.seek(pos)
        reader = csv.DictReader(csv_stream, dialect=dialect)
        rows = list(reader)
        self.fieldnames = reader.fieldnames
        # we need to convert the values to unicode
        for row in rows:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = unicode(value.decode(self.fileencoding)).encode('utf8')
        if len(rows)>0 and rows[0].has_key(''):
            for row in rows:
                if row.has_key(''):
                    row.pop('')
        return rows
