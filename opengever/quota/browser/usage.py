from opengever.quota import _
from opengever.quota.interfaces import IQuotaSizeSettings
from opengever.quota.sizequota import ISizeQuota
from Products.Five import BrowserView


def human_readable_size(num):
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if abs(num) < 1024.0:
            return '%3.1f %s' % (num, unit)
        num /= 1024.0

    return '%3.1f %s' % (num * 1024.0, unit)


def human_readable_limit(usage, limit):
    if limit == 0:
        return _(u'unlimited')

    return '{} ({})'.format(human_readable_size(limit),
                            '%.1f%%' % (usage * 100.0 / limit))


class UsageView(BrowserView):

    def get_size_infos(self):
        size_quota = ISizeQuota(self.context, None)
        settings = IQuotaSizeSettings(self.context, None)
        if size_quota is None or settings is None:
            return None

        usage = size_quota.get_usage()
        return {
            'size_usage': human_readable_size(usage),
            'soft_limit': human_readable_limit(
                usage, settings.get_soft_limit()),
            'hard_limit': human_readable_limit(
                usage, settings.get_hard_limit())}
