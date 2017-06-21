from contextlib import contextmanager
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import ticking_creator
from ftw.testing import freeze
from ftw.testing import staticuid


class OpengeverContentFixture(object):

    def __call__(self):
        with self.freeze_at_hour(7):
            self.create_users_and_units()

        with self.freeze_at_hour(8):
            self.create_repository_tree()

    def create_users_and_units(self):
        create(Builder('fixture').with_all_unit_setup())

    @staticuid('repotree')
    def create_repository_tree(self):
        create(Builder('repository_root').titled('Repository Root'))

    @contextmanager
    def freeze_at_hour(self, hour):
        """Freeze the time when creating content with builders, so that
        we can rely on consistent creation times.
        Since we can sort consistently when all objects have the exact same
        creation times we need to move the clock forward whenever things are
        created, using ftw.builder's ticking creator in combination with a
        frozen clock.

        In order to be able to insert new objects in the fixture without
        mixing up all timestamps, we group the builders and let each group
        start at a given hour, moving the clock two minutes for each builder.
        We move it two minutes because the catalog rounds times sometimes to
        minute precision and we want to be more precise.
        """
        with freeze(datetime(2016, 8, 31, hour, 1, 33)) as clock:
            with ticking_creator(clock, minutes=2):
                yield
