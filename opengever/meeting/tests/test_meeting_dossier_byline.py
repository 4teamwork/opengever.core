from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.tests import test_dossier_byline


class TestMeetingDossierByline(test_dossier_byline.TestDossierByline):

    def create_dossier(self):
        return create(Builder('meeting_dossier')
                      .in_state('dossier-state-active')
                      .having(reference_number_prefix='5',
                              responsible='hugo.boss',
                              start=date(2013, 11, 6),
                              end=date(2013, 11, 7),
                              external_reference='22900-2017'))
