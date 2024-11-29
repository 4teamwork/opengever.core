from opengever.nightlyjobs.runner import get_job_counts
from opengever.nightlyjobs.runner import get_nightly_run_timestamp
from opengever.nightlyjobs.runner import nightly_run_within_24h
from Products.Five.browser import BrowserView


def get_nightly_job_stats():
    job_counts = "\n".join(sorted(['{}: {}'.format(name, count)
                           for name, count in get_job_counts().items()]))
    nightly_status = 'Nightly status: {}'.format(
        'healthy' if nightly_run_within_24h() else 'unhealthy')
    timestamp = get_nightly_run_timestamp()
    last_nightly_run = 'Last nightly run: {}'.format(
        timestamp.isoformat() if timestamp else 'never')

    return '\n'.join([nightly_status, last_nightly_run, '\nNightly job counts:', job_counts])


class NightlyJobsStatsView(BrowserView):

    def __call__(self):
        return get_nightly_job_stats()
