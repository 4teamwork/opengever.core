from ftw.builder import builder_registry


class DummyClockTickBuilder(object):
    """A builder that does nothing.

    This may be used to still advance the clock when removing objects from
    the fixture.

    Because every builder object creation in the fixture uses a ticking_creator,
    removing objects from the fixture leads to the clock getting shifted for
    all objects that are created after the ones that got removed.

    This can lead to tons of tests failing, and lots of tedious, non-sensical
    work to just clean up their timestamps.

    Using this dummy builder the creation calls can just be stubbed out
    instead of being removed entirely.
    """

    def __init__(self, *args, **kwargs):
        pass

    def create(*args, **kwargs):
        pass


builder_registry.register('dummy_clock_tick', DummyClockTickBuilder)
