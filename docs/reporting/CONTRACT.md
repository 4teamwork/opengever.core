# Reporting Harness — Data Contract

This file is the **single source of truth** for the shape of the three JSON/Markdown
payloads the harness moves between layers. The `/report` skill
(`.claude/skills/project-report/SKILL.md`), the downstream **template** task
(`docs/reporting/template/`), and the **generation** task all conform to what is
written here. If a field changes, change it here first.

## The invariant — separation by writer

Every field has **exactly one writer**. No field is written by both a human and the
model. This is the whole point of the harness.

| Layer | File | Writer | Edited how |
|---|---|---|---|
| Operator | `docs/reporting/status.md` | **Human only** | Hand-edited Markdown + YAML front matter |
| Operator raw | `docs/reporting/hours.xlsx` | **Human only** | Dropped in from the time-tracking export |
| Harness | `docs/reporting/signals.json` | **Machine only** | Regenerated **wholesale** every run |
| Derived | `docs/reporting/report-data.json` | **Machine only** | Merge of operator + harness, per merge rules |
| Derived | `docs/reporting/report.html` | **Machine only** | Rendered from report-data.json |
| Derived | `docs/reporting/archive/report-YYYY-MM-DD.html` + `report-data-YYYY-MM-DD.json` | **Machine only** | Dated snapshots |

The operator NEVER edits `signals.json` / `report-data.json`. The harness NEVER edits
`status.md` / `hours.xlsx`. When the operator's override and the harness's estimate
disagree, the report **shows both** — neither writer touches the other's field.

**Dates.** Every date the report DISPLAYS is Swiss `dd.mm.yyyy`. The harness computes a
`_de` sibling for every date field it emits (`meta.report_date_de`,
`trajektorie.target_date_de`, `trajektorie.stretch_date_de`,
`trajektorie.history[].date_de`, `trajektorie.ideal.start_date_de`/`target_date_de`,
`ci.trend[].date_de`); the template renders only `_de` fields. ISO forms may remain for
machine use (sorting/dedup) but are never rendered.

---

## 1. Operator layer — `status.md` (human-written)

Front-matter fields (all operator-owned):

| Field | Type | Notes |
|---|---|---|
| `project_name` | string | Masthead title |
| `branch` | string | Exploratory long-lived branch (`ai-playground`). Merges are NOT a progress signal. |
| `target_date` | date `YYYY-MM-DD` | Zieltermin (fixed) |
| `stretch_date` | date `YYYY-MM-DD` \| "" | Streckungsende; blank = no stretch window |
| `budget_total_at` | number | Total budget in Arbeitstage (AT) |
| `hours_per_at` | number | Hours per AT, default `8` |
| `ampel` | `gruen`\|`gelb`\|`rot`\|`gelb-rot`\|"" | Operator management call; blank = show only harness signal |
| `ci_source` | `auto`\|`manual` | `auto` = query `gh` for GitHub check-runs (Jenkins posts each job as a check run on the commit) on the branch's origin head sha; `manual` = use the two fields below. `auto` works via the Checks API — the signal is JOB-level (named checks), not per-test counts (those require authenticated Jenkins access we don't have). Graceful degradation: if `gh` is unavailable/unauthenticated/returns no checks, falls back to the manual fields if set, else the CI KPI renders "nicht verfügbar" (kein erfundener Wert). |
| `ci_tests_total` | int | Only when `ci_source: manual` |
| `ci_tests_passed` | int | Only when `ci_source: manual` |
| `hours_columns` | map \| absent | Optional column mapping: `{person, week, hours, activity?}` |
| `hours_file` | glob string \| absent | Glob (relative to `docs/reporting/`) matching the dated weekly hours export, e.g. `hintergrund-tasks-stunden-*.xlsx`. The harness resolves this to the NEWEST matching file. Absent = default to `hours.xlsx`. |

Body tables (operator-owned rows):

- **Lieferbereiche**: `id, name, weight, progress_override, status_override, comment`
  (`progress_override` and `status_override` blank by default → harness estimate wins).
- **Stories**: `id, title, area, progress (0/25/50/75/100), status, next_proof, spec`.
- **Risiken**: `risiko, kategorie, auswirkung, wahrscheinlichkeit, fruehwarnsignal, naechste_aktion, owner, status`.
- **Scope-Cuts**: `prioritaet, massnahme, begruendung`. `prioritaet` MAY be a null/em-dash
  "—" sentinel marking a "Nicht schneiden" (do-not-cut) row instead of a numeric priority;
  renderers must tolerate a non-numeric/blank `prioritaet` rather than assume it is always
  an int. **Operator-only — not copied into `report-data.json` / the report.** Kept in
  `status.md` purely as the operator's own working notes on cut candidates; if you want it
  in the report again, it needs a dedicated section like Offene Entscheidungen got.
- **Prognose-Ampel-Override**: `bereich` (fixed keys `gesamtbeurteilung`, `projektfortschritt`,
  `kosten`, `personalaufwand`, `projektrisiken`), `verdict_override`, `begruendung_override`
  (both blank by default → harness verdict/reason wins, same override pattern as
  Lieferbereiche). This is the ONLY place a human can override a Prognose-Ampel row.
- **Offene Entscheidungen**: free list. Rendered as its own numbered section (08, see
  render contract in SKILL.md), placed just before Risiken.
- **Verlauf**: `date (YYYY-MM-DD), overall_progress_pct` — operator-known progress-history
  checkpoints (e.g. project start, prior dashboard snapshot). The harness MERGES these
  with archived `report-data.json` trajectory snapshots plus the current run, dedups by
  date (latest wins), sorted ascending, to build `trajektorie.history[]`. The current
  run's own point is added by the harness, not typed here.
- **Management Summary**: `summary_de` (operator-owned). Written for a manager scanning
  in 15 seconds: short bullet points, bold the key figure/word, cut fluff. Plain Markdown
  only — bullets as `- text` and emphasis as `**text**`, no raw HTML in status.md. The
  renderer (`render_report.py`, Step 6) converts this Markdown to `<ul><li>`/`<strong>`
  HTML when building `report.html`; `report-data.json` still carries the Markdown form
  verbatim (it is a derived/machine file, but the conversion itself happens at the final
  render step, not the merge step).

---

## 2. Harness layer — `signals.json` (machine-written, wholesale each run)

```jsonc
{
  "generated_at": "2026-07-09T14:55:00+02:00",  // ISO timestamp of this run
  "report_date": "2026-07-09",                   // run date (Stand)
  "branch": "ai-playground",                     // echoed from git / status.md

  "git": {
    "head_sha": "df869a4fc...",
    "commits_since_first_baseline": 42,
    "per_area_commit_hint": {                     // WEAK corroboration only, not progress
      "D0": 3, "D1": 27, "D2": 0, "D3": 0, "D4": 0, "D5": 0
    }
  },

  "specs": [                                      // from _bmad-output/**/spec-*.md front matter
    { "id": "background-tasks-infrastructure",
      "title": "Background Tasks Infrastructure",
      "status": "done", "created": "2026-06-12",
      "baseline_commit": "f07394dbf...", "path": "_bmad-output/implementation-artifacts/spec-...md" }
  ],

  "deferred": {                                   // from _bmad-output/**/deferred-work.md
    "open_count": 9,
    "items": [ { "source": "background-tasks-infrastructure", "title": "datetime.now() vs UTC ..." } ]
  },

  "ci": {                                         // see CI extraction rules in SKILL.md
    "source": "github-checks",                    // "github-checks" | "manual"
    "commit": "df869a4",                          // short origin head sha checks were read from
    "checks_total": 11,
    "checks_passed": 8,
    "checks_failed": 3,
    "pass_rate_pct": 72.7,                         // round(checks_passed / checks_total * 100, 1)
    "failing": [ { "name": "robot-tests", "url": "https://.../details" } ],
    "degraded": false,                            // true if gh unavailable AND no manual fallback
    "note": "Checks read from Jenkins via GitHub Checks API on origin head"
  },

  "areas": [                                      // ONE entry per delivery area D0..D5
    { "id": "D1",
      "progress_estimate": 27,                    // HARNESS LLM estimate 0..100 (never the override)
      "status_signal": "gelb-rot",               // harness-suggested colour
      "rationale": "Infra spec done + PR present, but no vertical slice; dispatcher/lock/notify absent." }
  ],

  "overall_progress_estimate": 13,                // Σ(weight × area.progress_estimate)/100, estimate-only

  "prognose": {                                   // 5-bereich forecast (named keys)
    "gesamtbeurteilung":  { "verdict": "gelb-rot", "reason": "..." },              // LLM synthesis, computed last
    "projektfortschritt": { "verdict": "gelb",     "reason": "Fortschritt vs. Zeit + Durchstich-Nachweis." }, // LLM
    "kosten":             { "verdict": "gelb",     "reason": "Budgetverbrauch vs. Earned Value." },          // LLM
    "personalaufwand":    { "verdict": "gruen",    "reason": "Budgetverbrauch 35% klar unter Fortschritt 59%." }, // MECHANICAL, see below
    "projektrisiken":     { "verdict": "gelb",     "reason": "Offene Risiken + verbleibende Scope-Cut-Reserve." } // LLM
  },

  "hours": {                                      // parsed & aggregated from hours.xlsx (empty if absent)
    "present": true,
    "hours_per_at": 8,
    "ist_stunden": 96.0,
    "ist_at": 12.0,
    "by_person": [ { "person": "Entwickler", "ist_stunden": 64.0, "ist_at": 8.0 } ],
    "by_week":   [ { "week": "2026-W27", "ist_stunden": 32.0, "ist_at": 4.0 } ],
    "rows_parsed": 12,
    "note": "Mapped via hours_columns"            // provenance / mapping note; parse warnings here
  }
}
```

`report_date`, `branch` and `overall_progress_estimate` use the **estimate only** — the
override merge happens in report-data.json.

---

## 3. Derived — `report-data.json` (machine-written merge, drives the template)

This is what the template renders. It also serves as the traceable, archived history
that feeds the CI-trend and trajectory charts.

```jsonc
{
  "meta": {
    "project_name": "Hintergrundtasks",
    "report_date": "2026-07-09",
    "report_date_de": "09.07.2026",              // Swiss display format
    "branch": "ai-playground",
    "generated_at": "2026-07-09T14:55:00+02:00"
  },

  "ampel": {
    "operator": "gelb-rot",                       // status.md `ampel` (may be "")
    "harness": "gelb-rot",                         // = signals.prognose.gesamt.verdict
    "display": "gelb-rot"                          // operator if set, else harness (masthead dot colour)
  },

  "summary_de": "- **Fortschritt:** … (plain Markdown bullets, HTML added only at render time)",

  "kpis": {
    "gesamtfortschritt_pct": 13,                  // overall_progress (override-merged)
    "budgetverbrauch_pct": 24.5,                  // ist_at / budget_total_at × 100
    "ci_pass_rate_pct": 72.7,                      // = ci.pass_rate_pct; KPI label "CI-Checks",
                                                    // displayed "checks_passed/checks_total gruen"
    "tage_bis_zieltermin": 38                      // working days report_date → target_date
  },

  "areas": [
    { "id": "D1", "name": "Framework + Operation 1 …", "weight": 30,
      "progress_estimate": 27,                    // from signals (harness)
      "progress_override": null,                  // from status.md (operator), null if blank
      "progress_final": 27,                       // override ?? estimate
      "progress_divergence": false,               // true if both present AND differ
      "status_override": null, "status_signal": "gelb-rot",
      "status_final": "gelb-rot",
      "contribution_pct": 8.1,                    // weight × progress_final / 100
      "rationale": "…", "comment": "…" }
  ],
  "overall_progress_pct": 13,                     // Σ(weight × progress_final)/100

  "stories": [                                    // operator rows, spec link resolved where present
    { "id": "S05", "title": "Persistente Task-Warteschlange …", "area": "D1",
      "progress": 75, "status": "gelb", "next_proof": "PR #8247 testbar …",
      "spec_path": "_bmad-output/implementation-artifacts/spec-...md", "spec_status": "done" }
  ],

  "prognose": {
    "items": [                                    // fixed order: gesamtbeurteilung first, then the other 4
      { "key": "gesamtbeurteilung", "label": "Gesamtbeurteilung",
        "verdict": "gelb-rot", "reason": "…",       // harness (signals.prognose.gesamtbeurteilung)
        "verdict_override": null, "reason_override": null,  // status.md Prognose-Ampel-Override row, null if blank
        "verdict_final": "gelb-rot", "reason_final": "…",   // override ?? harness
        "divergence": false },                      // true if either override is set
      { "key": "projektfortschritt", "label": "Projektfortschritt", "verdict": "gelb", "reason": "…",
        "verdict_override": null, "reason_override": null, "verdict_final": "gelb", "reason_final": "…",
        "divergence": false },
      { "key": "kosten", "label": "Kosten", "verdict": "gelb", "reason": "…",
        "verdict_override": null, "reason_override": null, "verdict_final": "gelb", "reason_final": "…",
        "divergence": false },
      { "key": "personalaufwand", "label": "Personalaufwand", "verdict": "gruen", "reason": "…",
        "verdict_override": null, "reason_override": null, "verdict_final": "gruen", "reason_final": "…",
        "divergence": false },
      { "key": "projektrisiken", "label": "Projektrisiken", "verdict": "gelb", "reason": "…",
        "verdict_override": null, "reason_override": null, "verdict_final": "gelb", "reason_final": "…",
        "divergence": false }
    ]
  },

  "budget": {
    "budget_total_at": 49, "hours_per_at": 8, "budget_total_hours": 392,
    "ist_stunden": 96.0, "ist_at": 12.0,
    "budgetverbrauch_pct": 24.5,
    "earned_value_at": 6.37,                      // overall_progress_pct/100 × budget_total_at
    "variance_at": -5.63,                          // earned_value_at − ist_at. Wert-gegen-Aufwand
                                                    // (Kosteneffizienz), KEINE Terminaussage. Negativ =
                                                    // mehr Aufwand verbucht als Wert erarbeitet.
                                                    // Schedule/Termin wird ueber die Prognose-Ampel und
                                                    // Fortschritt-vs-Zeit ausgedrueckt, nicht hier.
                                                    // Display label: "Wert vs. Ist-Aufwand"; caption:
                                                    // "Earned Value abzueglich verbuchtem Ist-Aufwand —
                                                    // Kosteneffizienz, keine Terminaussage."
    "by_person": [ /* from signals.hours */ ],
    "by_week":   [ /* from signals.hours */ ]
  },

  "ci": {
    "source": "github-checks", "commit": "df869a4",
    "checks_total": 11, "checks_passed": 8, "checks_failed": 3, "pass_rate_pct": 72.7,
    "failing": [ { "name": "robot-tests", "url": "…" } ],
    "degraded": false, "note": "…",
    "trend": [ { "date_de": "02.07.2026", "pass_rate_pct": 68.2 },
               { "date_de": "09.07.2026", "pass_rate_pct": 72.7 } ]  // current + archived snapshots
  },

  "risks":      [ { "risiko": "…", "kategorie": "…", "auswirkung": "…", "wahrscheinlichkeit": "…",
                    "fruehwarnsignal": "…", "naechste_aktion": "…", "owner": "…", "status": "…" } ],
  "offene_entscheidungen": [ "…" ],   // scope_cuts is NOT merged in — operator-only, stays in status.md

  "trajektorie": {
    "history": [ { "date_de": "12.06.2026", "overall_progress_pct": 0 },
                 { "date_de": "23.06.2026", "overall_progress_pct": 13 },
                 { "date_de": "09.07.2026", "overall_progress_pct": 13 } ],
                                                    // merged: operator Verlauf + archived
                                                    // report-data.json snapshots + current run,
                                                    // deduped by date, sorted ascending
    "ideal": { "start_date_de": "12.06.2026",       // = earliest history date
               "target_date_de": "31.08.2026" },    // reference line (start,0%) -> (target,100%)
    "target_date": "2026-08-31", "target_date_de": "31.08.2026",
    "stretch_date": "2026-09-14", "stretch_date_de": "14.09.2026"
  },

  "traceability": { "specs": [ /* signals.specs */ ], "deferred_open_count": 9, "head_sha": "…" }
}
```

### Merge / override rules (applied when building report-data.json)

1. **Per-area progress**: `progress_final = progress_override ?? progress_estimate`.
   If both present and they differ → set `progress_divergence: true` (the report shows
   both, e.g. `Modell: 27 % · erfasst: 20 %`). Neither field is overwritten.
2. **Per-area status colour**: `status_final = status_override ?? status_signal`.
3. **Overall progress**: `Σ(weight × progress_final)/100` over all areas.
4. **Ampel**: `display = operator ampel if non-empty, else harness prognose.gesamtbeurteilung`
   (masthead/summary traffic light; `status.md`'s `ampel` front-matter field).
4b. **Prognose-Ampel rows**: per row (`gesamtbeurteilung`, `projektfortschritt`, `kosten`,
   `personalaufwand`, `projektrisiken`): `verdict_final = verdict_override ?? verdict`,
   `reason_final = reason_override ?? reason`, `divergence = true` if either override is
   set (report shows the harness verdict/reason alongside as a footnote line). Overrides
   come from the operator's Prognose-Ampel-Override table in `status.md` — neither field
   is ever written by both writers.
   `personalaufwand.verdict` is the one MECHANICAL (non-LLM) row: `diff =
   kpis.gesamtfortschritt_pct - kpis.budgetverbrauch_pct`; `rot` if `diff < 0` (mehr
   Budget verbraucht als Fortschritt geliefert), `gelb` if `0 <= diff <= 10` (knapp
   beieinander), else `gruen`. Computed after Step 5 (KPIs must be final), still
   override-able via the same Prognose-Ampel-Override table.
5. **CI**: `source = manual` uses `ci_tests_*` from status.md (mapped to
   `checks_total`/`checks_passed`); otherwise the `gh` check-runs-derived numbers.
   `degraded: true` when neither is available.
6. **Trend / trajectory history**: read prior `report-data-*.json` in `archive/`, append
   the current run. De-duplicate by date (latest run of a day wins). Trajectory history
   additionally merges the operator `## Verlauf` checkpoints from status.md before
   dedup/sort. Every date in both series is emitted only as its `_de` (`dd.mm.yyyy`)
   form for display; the harness computes it from the underlying ISO date.
