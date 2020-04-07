Readonly-Mode Development Notes
===============================

The file ``readonly_development.patch`` contains a patch against
``development.cfg`` for a config that produces a minmal local ZEO setup,
with the ZEO client (instance) put in readonly mode.

Usage:

```
git apply docs/readonly_development.patch
bin/zeo start
bin/instance fg
```