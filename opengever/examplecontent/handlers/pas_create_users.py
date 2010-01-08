import csv

class SetupVarious(object):
    
    def __call__(self, setup):
        self.fileencoding = 'iso-8859-1'
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        members = self.create_users()
        self.create_groups(members)

    def create_users(self):
        members = []
        password = 'demo09'
        file = self.openDataFile('users.csv')
        users = self._get_objects_data(file)
        regtool = self.portal.portal_registration
        acl_users = self.portal.acl_users
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
            members.append(member)
            print '** created user', user['userid']
        return members

    def create_groups(self, members):
        groupstool = self.portal.portal_groups
        default = 'Sekretariat'
        groups = {
            # Sekretariat
            'Sachbearbeiter' : [
                'sachbearbeiter',
                ],
            'Vorsteher' : [
                'vorsteher'
                ],
            'Verwalter' : [
                'verwalter'
                ],
            'Administrators' : [
                'admin'
                ],
            }
        member_ids = [m.getProperty('username')
                      for m in members]
        assigned_members = []
        for gname,gmembs in groups.items():
            if groupstool.getGroupById(gname):
                continue
            groupstool.addGroup(gname)
            for mem in gmembs:
                groupstool.getGroupById(gname).addMember(mem)
                assigned_members.append(mem)
        if groupstool.getGroupById(default):
            return
        groupstool.addGroup(default)
        for mem in member_ids:
            if mem not in assigned_members:
                groupstool.getGroupById(default).addMember(mem)
                assigned_members.append(mem)


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
                    row[key] = unicode(value.decode(self.fileencoding))
        if len(rows)>0 and rows[0].has_key(''):
            for row in rows:
                if row.has_key(''):
                    row.pop('')
        return rows
