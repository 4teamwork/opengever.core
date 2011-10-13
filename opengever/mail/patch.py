

# XXX: Temporary fix for Title accessor
# return unicode instead of utf-8 bytestring
# because other opengever types to the same
def Title(self):

    if isinstance(self.title, str):
        return self.title.decode('utf-8')
    return self.title
