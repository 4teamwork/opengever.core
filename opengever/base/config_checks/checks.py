class BaseCheck(object):
    def __init__(self, context):
        self.context = context

    @property
    def check_id(self):
        return self.__class__.__name__

    def config_error(self, title, description=''):
        return {
            'id': self.check_id,
            'title': title,
            'description': description,
        }
