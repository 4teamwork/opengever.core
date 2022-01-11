# Running the testserver with Docker

## Overview

Because the testserver requires some services (such as solr, sablon, etc),
it should be run with **docker compose**.

The `docker compose.yml` in the root of `opengever.core` includes the necessary definitions
for running the testserver in docker.

## Usage

Start testserver:

```
$ cd opengever.core
$ docker compose up testserver
$ bin/testserverctl isolate
```

You can also run `testserverctl` from within docker:

```
docker compose exec testserver bin/testserverctl isolate
```

After executing the ``isolate`` command you can open http://localhost:55001/plone


## Build image

```
$ cd opengever.core
$ docker compose build testserver
```

The image needs to be built manually at the moment.
Published images may not be up to date.
