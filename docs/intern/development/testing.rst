Testing
=======

Performance analysis
====================

We provide convenience scripts to measure the throughput, performance and
relative and absolute runtime weights of various combinations of our testing
stack. These are usually run once per release to try to spot any obvious jumps
in performance for the better or worse. The results are also used as a basis to
inform us on how to optimise the parallel running of the tests on our CI
infrastructure.

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