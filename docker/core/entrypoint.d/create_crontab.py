# Create crontab file with start times depending on deployment number to avoid
# starting cron jobs at the same time.
from os import environ


# Cron jobs: tuples of (from, until, cmd)
CRON_JOBS = [
    ('22', '22:30', '/app/bin/zopectl -C /app/etc/zope.conf dump_content_stats --python-du -d /data --filestorage-path filestorage/Data.fs --blobstorage-path blobstorage'),
    ('23', '24', '/app/bin/zeopack -d 7 zeoserver:8100'),
    ('1', '2', '/app/bin/zopectl -C /app/etc/zope.conf run_nightly_jobs'),
    ('4', '4:20', '/app/bin/zopectl -C /app/etc/zope.conf generate_remind_notifications'),
    ('4:30', '4:50', '/app/bin/zopectl -C /app/etc/zope.conf generate_overdue_notifications'),
    ('6', '6:15', '/app/bin/zopectl -C /app/etc/zope.conf send_digest'),
]


def safe_int(value, default=1):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_minutes(value):
    hours = int(value.split(':')[0])
    minutes = 0
    if ':' in value:
        minutes = int(value.split(':')[1])
    return hours * 60 + minutes


def main():
    if environ.get('CRON_SKIP_GENERATION', '').lower() in ['1', 'true', 'yes']:
        return

    start_slot = safe_int(environ.get('CRON_START_SLOT', environ.get('DEPLOYMENT_NUMBER', '01')))
    max_start_slots = safe_int(environ.get('CRON_MAX_START_SLOTS', '12'), default=12)
    start_slot = (start_slot - 1) % max_start_slots + 1

    with open('/app/cron/crontab', 'w') as cronfile:
        for job in CRON_JOBS:
            from_minutes = parse_minutes(job[0])
            until_minutes = parse_minutes(job[1])
            window_minutes = until_minutes - from_minutes
            delta = window_minutes / float(max_start_slots)
            start_minutes = from_minutes + delta * (start_slot - 1)
            hours = int(start_minutes // 60)
            minutes = int(start_minutes % 60)
            cronfile.write('{} {} * * * {}\n'.format(minutes, hours, job[2]))


if __name__ == "__main__":
    main()
