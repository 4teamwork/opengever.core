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

It will also produce a log file named like
``2019-05-01-layerperf.log``.
