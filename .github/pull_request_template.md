_PR-Description: should contain all the information necessary for an outsider to understand the change without looking at the code or the issue!_

- _Why the change is necessary_
- _What the goal of the change is_
- _How change is achieved (e.g. design decisions)_
- _The author should advertise and sell the change in the PR body_

_Screenshot: whenever useful, but only as a visual aid._


Definition of Done: https://4teamwork.atlassian.net/wiki/spaces/CHX4TW/pages/917562/


## Checklist (Must have)

_Everything has to be done/checked. Checked but not present means the author deemed it unnecessary._

- [ ] Changelog entry
- [ ] Link to issue (Jira or GitHub) and backlink in issue (Jira)


## Checklist (if applicable)

_Only applicable should be left and checked._

- API change:
  - [ ] Documentation is updated
  - If breaking:
    - [ ] api-change label added
    - [ ] Scrum master is informed
- New functionality:
  - [ ] for `document` also works for `mail`
  - [ ] for `task` also works for `forwarding`
- Upgrade steps (changes in profile):
  - [ ] Make it deferrable if possible
  - [ ] Execute as much as possible conditionally
- DB-Schema migration
  - [ ] All changes on a model (columns, etc) are included in a DB-schema migration.
  - [ ] Constraint names are shorter than 30 characters (`Oracle`)
- [ ] Change could impact client installations, client policies need to be adapted
- New translations
  - [ ] All msg-strings are unicode
- Change in schema definition:
  - [ ] If `missing_value` is specified, then `default` has to be set to the same value
