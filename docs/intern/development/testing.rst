Testing
=======

Local
-----

In case of amending the fixture for the integration tests, it can sometimes be
advantageous and quicker to run a local script for validating the changes to
tests from a fixture change. Such a scenario usually involves severely messy
and large error outputs from the CI. For such cases, we provide the script
``bin/amend-fixture``.

CI
--

We run the tests with our in-repo test runner ``bin/mtest``. It is a Python
script, which discovers all the tests and splits those up to suitable test run
chunks. As we also split within a test layer, it unfortunately requires some
baked in knowledge about what to split up and with what kinds of constraints.
It can also be used for local test runs and understands the same ``--layer``
and ``-m`` parameters as ``zope.testrunner`` does and these are used only in
the test discovery phase of the run.

Performance analysis
====================

We provide convenience scripts to measure the throughput, performance and
relative and absolute runtime weights of various combinations of our testing
stack. These are usually run once per release to try to spot any obvious jumps
in performance for the better or worse. The results are also used as a basis to
inform us on how to optimise the parallel running of the tests on our CI
infrastructure.

We provide a helper script, which runs all of them at once: ::

  $ bin/performance-analysis
  -- snip --
  real    191m7.929s
  user    919m21.400s
  sys     63m57.496s

It will also provide 4 log files named like: ::

  2019-05-01-layerperf.log
  2019-05-01-moduleperf.log
  2019-05-01-classperf.log
  2019-05-01-testperf.log


Measuring test layer performance
--------------------------------

The script to time the layers is usually used to see if we have an incentive
to kill a particular testing layer in favor of porting it to either the main
unfixturised functional test layer or the fixturised integration test layer.

Here is an example run of it being run for two layers: ::

  bin/time-layers --layer 'zope.testrunner.layer.UnitTests' --layer 'opengever.core.testing.opengever:core:memory_db'
                                            layer          cnt               spd            rt       rt%      cnt%        wt%
  ===========================================================================================================================
                  zope.testrunner.layer.UnitTests    294 tests    0.013 s / test    03 seconds    38.18%    52.69%     72.46%
  opengever.core.testing.opengever:core:memory_db    264 tests    0.023 s / test    06 seconds    61.82%    47.31%    130.67%
  ---------------------------------------------------------------------------------------------------------------------------
  Sorted by runtime.

  Total:     09 seconds
  Wallclock: 25 seconds

It will also produce a log file named like ``2019-05-01-layerperf.log``.

Measuring test performance per layer/module
-------------------------------------------

The script to time the modules per layer is usually used to see where the bulk
weight of the test runtime is spent and to see if there are any meaningful
abnormally heavy corners of our stack to tackle. The speed of the modules at
around the 100% weight mark of the whole test run is a good thing to keep track
of.

Here is an example run of it being run for two modules: ::

  bin/time-modules-layers -m 'opengever.inbox' -m 'opengever.journal'
                                              layer               module         cnt               spd                       rt       rt%      cnt%        wt%
  ============================================================================================================================================================
                    zope.testrunner.layer.UnitTests      opengever.inbox    16 tests    0.001 s / test               00 seconds     0.00%    11.03%      0.03%
               opengever.core.testing.ActivityLayer      opengever.inbox    10 tests    3.603 s / test               36 seconds    17.32%     6.90%    251.07%
  opengever.core.testing.opengever.core:integration      opengever.inbox    35 tests    1.542 s / test               53 seconds    25.94%    24.14%    107.46%
   opengever.core.testing.opengever.core:functional    opengever.journal    38 tests    1.462 s / test               55 seconds    26.70%    26.21%    101.90%
   opengever.core.testing.opengever.core:functional      opengever.inbox    46 tests    1.359 s / test    01 minutes 02 seconds    30.04%    31.72%     94.69%
  ------------------------------------------------------------------------------------------------------------------------------------------------------------
  Sorted by runtime.

  Total:     03 minutes 28 seconds
  Wallclock: 02 minutes 53 seconds

It will also produce a log file named like ``2019-05-01-moduleperf.log``.

Measuring test performance per test class
-----------------------------------------

The script to time the test classes is usually used to see if we have any
disproportionately long running test classes. This is meaningful for our CI
stack as we split and parallelise the running of the tests on a per test class
basis with the assumption of similar runtimes per test class on average. Some
of the problematic-for-splitting test classes have been moved from layer to
layer or isolated onto their own layer from time to time to fetch a low hanging
wall clock time saving for the CI test runs.

Here is an example run of it being run for one module: ::

  bin/time-classes -m 'opengever.inbox'
                                                                     classname         cnt               spd            rt       rt%      cnt%        wt%
  =======================================================================================================================================================
               opengever.inbox.tests.test_transitioncontroller.TestRefuseGuard     4 tests    0.000 s / test    00 seconds     0.00%     3.74%      0.02%
                opengever.inbox.tests.test_transitioncontroller.TestCloseGuard     2 tests    0.001 s / test    00 seconds     0.00%     1.87%      0.04%
               opengever.inbox.tests.test_transitioncontroller.TestAcceptGuard     4 tests    0.000 s / test    00 seconds     0.00%     3.74%      0.02%
             opengever.inbox.tests.test_transitioncontroller.TestReassignGuard     2 tests    0.001 s / test    00 seconds     0.00%     1.87%      0.04%
      opengever.inbox.tests.test_transitioncontroller.TestAssignToDossierGuard     2 tests    0.001 s / test    00 seconds     0.00%     1.87%      0.04%
       opengever.inbox.tests.test_transitioncontroller.TestReassignRefuseGuard     2 tests    0.001 s / test    00 seconds     0.00%     1.87%      0.04%
                     opengever.inbox.tests.test_refuse.TestRefusingForwardings     3 tests    0.048 s / test    00 seconds     0.10%     2.80%      3.73%
                      opengever.inbox.tests.test_tabs.TestAssignedInboxTaskTab     2 tests    0.259 s / test    00 seconds     0.38%     1.87%     20.27%
                        opengever.inbox.tests.test_tabs.TestIssuedInboxTaskTab     2 tests    0.276 s / test    00 seconds     0.40%     1.87%     21.56%
  opengever.inbox.tests.test_inbox_bumblebee_gallery.TestInboxBumblebeeGallery     1 tests    0.710 s / test    00 seconds     0.52%     0.93%     55.56%
                           opengever.inbox.tests.test_tabs.TestInboxTabbedview     3 tests    0.332 s / test    00 seconds     0.73%     2.80%     26.00%
        opengever.inbox.tests.test_transition_actions.TestReassignRefuseAction     1 tests    1.339 s / test    01 seconds     0.98%     0.93%    104.77%
       opengever.inbox.tests.test_transition_actions.TestAssignToDossierAction     1 tests    1.369 s / test    01 seconds     1.00%     0.93%    107.12%
                opengever.inbox.tests.test_transition_actions.TestAcceptAction     1 tests    1.380 s / test    01 seconds     1.01%     0.93%    107.98%
     opengever.inbox.tests.test_transition_actions.TestReassignToDossierAction     1 tests    1.392 s / test    01 seconds     1.02%     0.93%    108.92%
                 opengever.inbox.tests.test_transition_actions.TestCloseAction     1 tests    1.401 s / test    01 seconds     1.02%     0.93%    109.62%
                         opengever.inbox.tests.test_tabs.TestClosedForwardings     1 tests    1.410 s / test    01 seconds     1.03%     0.93%    110.33%
                opengever.inbox.tests.test_transition_actions.TestRefuseAction     1 tests    1.487 s / test    01 seconds     1.09%     0.93%    116.35%
                    opengever.inbox.tests.test_yearfolder.TestYearFolderStorer     1 tests    2.301 s / test    02 seconds     1.68%     0.93%    180.05%
                      opengever.inbox.tests.test_inbox_container.TestInboxView     3 tests    0.804 s / test    02 seconds     1.76%     2.80%     62.94%
                opengever.inbox.tests.test_move_items.TestMoveItemsWithBrowser     1 tests    2.708 s / test    02 seconds     1.98%     0.93%    211.89%
                     opengever.inbox.tests.test_accept.TestForwardingAccepting     1 tests    3.063 s / test    03 seconds     2.24%     0.93%    239.67%
      opengever.inbox.tests.test_activities.TestForwardingActivitesIntegration     1 tests    3.140 s / test    03 seconds     2.30%     0.93%    245.69%
                 opengever.inbox.tests.test_inbox_container.TestInboxContainer     3 tests    1.172 s / test    03 seconds     2.57%     2.80%     91.71%
                    opengever.inbox.tests.test_yearfolder.TestYearFolderGetter     4 tests    0.903 s / test    03 seconds     2.64%     3.74%     70.70%
                                    opengever.inbox.tests.test_inbox.TestInbox     8 tests    0.807 s / test    06 seconds     4.72%     7.48%     63.14%
         opengever.inbox.tests.test_overview.TestInboxOverviewIssuedInboxTasks     3 tests    2.157 s / test    06 seconds     4.73%     2.80%    168.78%
       opengever.inbox.tests.test_overview.TestInboxOverviewAssignedInboxTasks     4 tests    1.887 s / test    07 seconds     5.52%     3.74%    147.67%
                 opengever.inbox.tests.test_refuse.TestRefuseForwardingStoring     5 tests    1.518 s / test    07 seconds     5.55%     4.67%    118.76%
                     opengever.inbox.tests.test_api_support.TestAPITransitions     5 tests    1.526 s / test    07 seconds     5.58%     4.67%    119.40%
                  opengever.inbox.tests.test_inbox_assign.TestAssignForwarding     4 tests    2.060 s / test    08 seconds     6.02%     3.74%    161.17%
                          opengever.inbox.tests.test_forwarding.TestForwarding     8 tests    1.108 s / test    08 seconds     6.48%     7.48%     86.69%
              opengever.inbox.tests.test_overview.TestInboxOverviewDocumentBox     5 tests    1.773 s / test    08 seconds     6.48%     4.67%    138.70%
                 opengever.inbox.tests.test_activities.TestForwardingActivites     3 tests    3.101 s / test    09 seconds     6.80%     2.80%    242.67%
          opengever.inbox.tests.test_activities.TestForwardingReassignActivity     3 tests    4.254 s / test    12 seconds     9.33%     2.80%    332.86%
                         opengever.inbox.tests.test_workflow.TestInboxWorkflow    11 tests    1.779 s / test    19 seconds    14.31%    10.28%    139.17%
  -------------------------------------------------------------------------------------------------------------------------------------------------------
  Sorted by runtime.

  Total:     02 minutes 16 seconds
  Wallclock: 07 minutes 46 seconds

It will also produce a log file named like ``2019-05-01-classperf.log``.

Measuring test performance per test method
------------------------------------------

The script to time the test methods is usually used to see if we have any
disproportionately long running tests. This has been very useful for spotting
tests where we can save time by using the fixture and porting the test class to
the fixturised integration test layer and also for spotting any tests where we
can use the fixtures in a more clever way. A good example of the latter is
spotting content moving tests being slower than they should be and simply
having them use different objects from the fixture.

For runtime considerations, this script is implemented differently as a simple
shell script / pipeline. If we'd use the same method for this as we use for the
other timing scripts, the time spent on rediscovering the tests once per test
method would make the runtime unusably long.

If one wants to run a local metrification run of a subset of our tests, one has
to take a look at ``bin/time-tests`` and adapt it to their needs manually as a
shell oneliner.

Here is an example run of it being run for one module: ::

  $ time bin/test -m opengever.portlets -vvv 2>/dev/null | grep -E '\([0-9]+\.[0-9]+ s\)' | awk '{print $3, $2, $1}' | tr -d '()' | sort -k1 -n | tee 2019-05-01-testperf.log
  0.000 opengever.portlets.tree.tests.test_favorites.TestRepositoryFavoritesETagValue test_etag_value_for_anonymous
  0.016 opengever.portlets.tree.tests.test_favorites.TestRepositoryFavoritesETagValue test_etag_value_invalidates_on_delete_favorite
  0.022 opengever.portlets.tree.tests.test_favorites.TestRepositoryFavoritesETagValue test_etag_value_invalidates_on_add_favorite
  0.138 opengever.portlets.tree.tests.test_favorites.TestRepositoryFavoritesETagValue test_etag_is_eqaul_if_nothing_changed
  0.482 opengever.portlets.tree.tests.test_treeportlet.TestTreePortlet test_favorite_tab_is_rendered_when_favorites_are_enabled
  0.537 opengever.portlets.tree.tests.test_treeportlet.TestTreePortlet test_favorite_tab_is_not_rendered_when_favorites_are_disabled
  1.324 opengever.portlets.tree.tests.test_treeportlet.TestTreePortlet test_context_url_data_object_is_absolute_url_of_current_context

  real    0m28,408s
  user    0m18,103s
  sys     0m10,239s

It will also produce a log file named like ``2019-05-01-testperf.log``.

Profiling
=========

Profiling a local instance
--------------------------

Assuming the first python on your ``$PATH`` is the same with which you have
built out the instance, start the instance with
``python -m cProfile -o instance.prof bin/instance fg``, do your thing and shut
the instance down.

The profiling result file ``instance.prof`` will be in your current working
directory.

Profiling the tests
-------------------

For profiling the tests, we provide a convenience shell script
``bin/profile-tests``, which profiles the fixture generation and all the module
/ layer permutations independent of each other. It modifies the run order of
the layers to enable the use of the fixture for all the fixturised layers.

The result files will be prefixed with the current date and the git commit hash
of ``HEAD`` and can be found in ``parts/test/*prof``.

A good starting point for digging into the results is setting the root of your
view onto the test function, immediately under which are all the tests which
have gotten run and then zooming in test by test and resetting the zoom to get
back to the root.

Viewing profiling results
-------------------------

The results may be browsed by obtaining a profiling result visualizer and
pointing that at a profiling result file (``.prof``). The modern option with
easier installability and better usability is SnakeViz_, but as it is
Tornado_ and browser based, sometimes in the case of very complex and deep
views, it'll hit the DOM element count limits of modern browsers. Sorting is
also an exercise in patience and the UX is not the best, but one can make do.

The inherent benefit is the easy installability into a virtualenv by simply
doing a ``pip install -U setuptools pip snakeviz``. Works in both Python 2 and
3.

.. _Tornado: https://www.tornadoweb.org/
.. _SnakeViz: https://jiffyclub.github.io/snakeviz/

In case there are hard limits in regards to the usability of SnakeViz one
cannot get around, the venerable GUI application RunSnakeRun_ is still
functional and can still be installed into a Python 2.7 virtualenv via
``pip install -U setuptools pip SquareMap RunSnakeRun``. It will require a
``wx`` installation at install time and this can be obtained from homebrew_
via ``brew install wxmac``.

.. _RunSnakeRun: http://www.vrplumber.com/programming/runsnakerun/
.. _homebrew: https://brew.sh/

It can also sometimes be advantageous to take a look at the profiling results
with KCachegrind_. This will require one to convert the ``cProfile`` results to
a Valgrind_ style calltree with pyprof2calltree_.

.. _KCachegrind: https://kcachegrind.github.io/html/Home.html
.. _Valgrind: http://www.valgrind.org/
.. _pyprof2calltree: https://github.com/pwaller/pyprof2calltree
