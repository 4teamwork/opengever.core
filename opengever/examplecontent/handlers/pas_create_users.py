import csv

class SetupVarious(object):
    
    def __call__(self, setup):
        self.fileencoding = 'utf8'
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.create_users()
        self.set_roles()

    def active(self, setup):
        return setup.openDataFile('users.csv') and True or \
            setup.openDataFile('roles.csv') and True

    def create_users(self):
        password = 'demo09'
        file = self.openDataFile('users.csv')
        if not file:
            return
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
                (),
                None,
                properties={
                    'username' : user['userid'],
                    'email' : user['email'],
                    }
                )
            member.setMemberProperties({
                    'fullname' : '%s %s' % (
                        user['lastname'],
                        user['firstname'],
                        )
                    })
            # groups are comma-seperated
            for gid in user['groups'].split(','):
                gid = gid.strip()
                if not groupstool.getGroupById(gid):
                    groupstool.addGroup(gid)
                    print '** created group', gid
                groupstool.getGroupById(gid).addMember(user['userid'])
            print '** created user', user['userid']

    def set_roles(self):
        print '* setting roles (roles.csv)'
        file = self.openDataFile('roles.csv')
        groupstool = self.portal.portal_groups
        acl_users = self.portal.acl_users
        if not file:
            return
        entries = self._get_objects_data(file)
        for entry in entries:
            if not entry['location'] or len(entry['location'])==0:
                global_role = True
            else:
                global_role = False
                obj = self.get_object_by_pathish_title(entry['location'])
                if not obj:
                    print '** could not find obj at', entry['location']
                    continue
            group = groupstool.getGroupById(entry['user_or_group'])
            user = acl_users.getUserById(entry['user_or_group'])
            if not group and not user:
                print '** could not find group/user', entry['user_or_group']
                continue
            roles = [r.strip() for r in entry['roles'].split(',')]
            if global_role:
                acl_users.portal_role_manager.assignRolesToPrincipal(roles,
                                                                     entry['user_or_group'])
                print 'Assigned', entry['user_or_group'], 'to roles', roles
            else:
                obj.manage_setLocalRoles(entry['user_or_group'], roles)
                print 'Set local roles at', obj, ':', roles, 'for', entry['user_or_group']
        # catalog
        #print '** update catalog'
        #self.portal.portal_catalog.manage_catalogReindex()

    def get_object_by_pathish_title(self, title, container=None, title_attribute='title'):
        if not container:
            container = self.portal
        if not title:
            return container
        parts = title.split('/')
        next_title = parts[0].strip()
        if not next_title:
            return container
        for id in container.objectIds():
            obj = container.get(id)
            title = getattr(obj, title_attribute,
                            getattr(obj, 'title',
                                    getattr(obj, 'Title', None)))
            if not title:
                continue
            if isinstance(title, str) or isinstance(title, unicode):
                title = title.strip()
            if title==next_title:
                if len(parts)==1:
                    return obj
                else:
                    return self.get_object_by_pathish_title('/'.join(parts[1:]),
                                                            container=obj,
                                                            title_attribute=title_attribute)
        return None

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
