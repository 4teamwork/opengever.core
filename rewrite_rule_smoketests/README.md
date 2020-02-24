### Usage

Run

```bash
bin/zopepy rewrite_rule_smoketests/smoketests.py
```

to execute the smoke tests. Some tests will require credentials,
and will therefore be skipped. In order to provide those credentials
(one pair per cluster), run

```bash
bin/zopepy rewrite_rule_smoketests/smoketests.py --prompt-credentials
``

The credentials (username and password) will then be used to log into
the cluster's corresponding portal, get a session, and store those
session cookies to `~/.opengever/rewrite_rule_smoketests/session_cookies.json`.

The password itself will never be stored.
