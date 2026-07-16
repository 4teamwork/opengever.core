---
name: project-report
description: 'Generate the Hintergrundtasks project-status report (HTML, Swiss design, German). Use when the user says "generate project report", "/report", "update the status report", or "erzeuge den Projektbericht". Reads the operator layer (docs/reporting/status.md), gathers machine signals from BMAD specs + git + CI + the hours export, reconciles per-area LLM estimates with operator overrides, and renders a self-contained HTML report plus a dated archive snapshot.'
---

# Project Report Harness

**Goal:** Produce a repeatable, self-contained HTML project-status report for the
"Hintergrundtasks" (background-tasks) project — a reporting harness whose defining
principle is **separation by writer**.

## THE INVARIANT — separation by writer (read first, never violate)

Every data field has **exactly ONE writer**. No field is ever written by both a human
and the model.

- **Operator layer (human only):** `docs/reporting/status.md` (Markdown + YAML front
  matter) and `docs/reporting/hours.xlsx` (raw time-tracking export). The harness READS
  these and NEVER writes them.
- **Harness layer (machine only):** `docs/reporting/signals.json`, regenerated
  **wholesale** every run. The human NEVER edits it. That is why signals live in a
  separate file, not a section of status.md — the harness overwrites its own data each
  run and must never clobber hand-edited prose or create noisy diffs.
- **Derived (machine only):** `report-data.json` (merge), `report.html`, and dated
  archive snapshots.

When an operator override and a harness estimate disagree, the report **shows both** —
the harness never writes into an operator field and vice versa. The authoritative field
map and JSON schemas live in **`docs/reporting/CONTRACT.md`**; read it alongside this
skill.

## Critical project constraint

This is an **exploratory project on a single long-lived branch (`ai-playground`) that
will NOT be merged until very late**. Therefore **merged PRs are NOT a progress signal**
— never compute progress from merges. The one objective signal is the **CI-Checks pass
rate** (checks_passed/checks_total) on the origin head commit, sourced from GitHub
check-runs that Jenkins posts, treated as a distinct QUALITY/health metric, separate
from the (subjective, weighted) progress metric.

## Files & paths

| Role | Path |
|---|---|
| Operator front matter + tables | `docs/reporting/status.md` |
| Operator raw time export | `docs/reporting/hours.xlsx` |
| Harness signals (wholesale) | `docs/reporting/signals.json` |
| Merged render dataset | `docs/reporting/report-data.json` |
| Rendered report | `docs/reporting/report.html` |
| Archive snapshots | `docs/reporting/archive/report-YYYY-MM-DD.html`, `report-data-YYYY-MM-DD.json` |
| HTML template | `docs/reporting/template/report.html.tmpl` (built by the template task) |
| Renderer (Step 6) | `.claude/skills/project-report/render_report.py` (report-data.json + template → report.html) |
| Data contract / schemas | `docs/reporting/CONTRACT.md` |
| Auto sources | `_bmad-output/**` (specs + `deferred-work.md`), `git`, `gh` |

## Output language & design

- **Report language: German, Swiss convention — echte Umlaute ä/ö/ü verwenden, aber KEIN
  ß — immer "ss".** Labels and narrative in German. (This skill file and CONTRACT.md are
  English engineering docs; the rendered report is German.)
- **Dates: Swiss `dd.mm.yyyy` everywhere displayed.** Every date the report SHOWS is
  formatted `dd.mm.yyyy`. The harness computes `_de` variants for every date field
  (`meta.report_date_de`, `trajektorie.target_date_de`, `trajektorie.stretch_date_de`,
  `trajektorie.history[].date_de`, `ci.trend[].date_de`); the template only ever renders
  `_de` fields. ISO forms may remain in the data for machine use (sorting, diffing), but
  nothing ISO is rendered.
- **Design: Swiss International Typographic Style**, reusing the token/type/ledger/chart
  system from the reference mockup at `/home/mca/Downloads/mockup-swiss.html`
  (single red accent `#e30613`, light/dark "Invert" theme, numbered sections, data-ink
  SVG charts, mono kicker). Bilingual kicker pattern **flipped**: German primary, mono
  English kicker as secondary. The template must be **self-contained** — all CSS/JS
  inline, no external requests.
- **Writing style: write for a manager, not an engineer.** Every prose field that ends up
  in the report — `summary_de`, per-area `comment`, Prognose-Ampel `reason` — is read by
  someone who wants the pace and state of the project in seconds, not a technical
  narrative. Short sentences or bullet points, bold the key figure/word, cut fluff and
  detail that doesn't change a management decision (no file/function names, no
  implementation blow-by-blow). `summary_de` should default to a bullet list covering:
  Fortschritt, Kernnutzen, Budget, offene Punkte, Risiko, Ampel-Empfehlung. One line each.
  Write it as **plain Markdown** (`- text`, `**bold**`) in `status.md` — never raw HTML.
  The renderer converts Markdown to HTML at Step 6 (see CONTRACT.md §1).

---

## Pipeline

Run these steps in order. Degrade gracefully at every external boundary (gh, xlsx, git);
never abort the whole run because one source is missing — record the gap in a `note`/
`degraded` field and continue.

### Step 1 — Load the operator layer

1. Read `docs/reporting/status.md`. Parse the YAML front matter and every body table
   (Lieferbereiche, Stories, Risiken, Scope-Cuts, Offene Entscheidungen, Management
   Summary). Schema below.
2. If `status.md` is missing or still the empty skeleton (no seeded areas), tell the user
   to seed it first and stop.
3. Treat everything from status.md as operator-owned and immutable in this run.

### Step 2 — Gather machine signals (→ signals.json)

Build `signals.json` fresh (do not read the previous one except archives for trends).

1. **BMAD specs** — glob `_bmad-output/**/spec-*.md`; parse each front matter
   (`title`, `status`, `created`, `baseline_commit`). Record as `specs[]`.
2. **Deferred work** — parse `_bmad-output/**/deferred-work.md`; count open items
   (each bullet under a `## From:` heading) → `deferred.open_count` + `items[]`.
3. **git** — `git rev-parse HEAD`; for each spec, `git log <baseline_commit>..HEAD
   --oneline` to gauge activity. Derive a **weak** `per_area_commit_hint` by matching
   changed paths/spec topics to areas — corroboration only, never the progress number.
4. **CI** — see "CI extraction" below → `ci{}`.
5. **hours.xlsx** — see "hours ingestion" below → `hours{}`.

### Step 3 — Per-area LLM assessment & reconciliation

For each delivery area D0–D5 (from status.md), the **harness** produces:

- `progress_estimate` (0–100): an LLM estimate grounded in code changes on the branch
  + BMAD spec status (`done`/in progress) + deferred-work load. Corroborate — do not
  drive — with `per_area_commit_hint`.
- `status_signal`: suggested colour (`gruen`/`gelb`/`gelb-rot`/`rot`/`grau`).
- `rationale`: one honest sentence citing the evidence.

Write these to `signals.areas[]`. Compute `overall_progress_estimate =
Σ(weight × progress_estimate)/100` (estimate-only).

Then evaluate the **5-bereich Prognose-Ampel** (harness verdict, German reasons). Four of
the five rows are LLM judgment calls; **Personalaufwand is mechanical** (a fixed formula,
not a judgment call — see Step 5) and **Gesamtbeurteilung is a synthesis** written last,
once Personalaufwand's computed verdict is known. Evaluate now:

1. **Projektfortschritt** — weighted progress vs. calendar progress (elapsed working
   days / total to target_date), folding in whether a real operation runs end-to-end
   (Durchstich) and not just infrastructure (evidence: a spec whose intent is a
   user-visible mutation is `done` AND exercised).
2. **Kosten** — budget efficiency: Earned Value vs. Ist-Aufwand (`variance_at`) and
   `budgetverbrauch_pct` vs. `overall_progress_pct`. Verdict degrades when cost is
   running ahead of delivered value.
3. **Projektrisiken** — aggregate of the operator Risiken list (weight by
   Auswirkung × Wahrscheinlichkeit) plus whether realistic Scope-Cut candidates remain
   without losing the core goal (read the operator Scope-Cuts list).

Rules: **Gruen** = roughly on plan, next critical proof realistic within 1 week.
**Gelb** = behind, but scope-cuts/stretch can still save the date. **Rot** = the critical
vertical slice is missing or a blocker is open > 1 week. Write these three to
`signals.prognose` as named entries (`projektfortschritt`, `kosten`, `projektrisiken`),
each `{verdict, reason}`. `personalaufwand` and `gesamtbeurteilung` are added in Step 5,
after the KPIs they depend on are final.

> This is the ONLY writer of `progress_estimate` and the Prognose-Ampel. The operator's
> `progress_override`, `status_override`, `ampel`, and the Prognose-Ampel-Override table
> are separate fields in status.md.

### Step 4 — Merge into report-data.json (apply override rules)

Per `CONTRACT.md` merge rules:

1. `progress_final = progress_override ?? progress_estimate`; set
   `progress_divergence` when both present and differ (report shows both).
2. `status_final = status_override ?? status_signal`.
3. `overall_progress_pct = Σ(weight × progress_final)/100`.
4. `ampel.display = operator ampel if non-empty, else prognose.gesamtbeurteilung`; keep
   both. Build `prognose.items[]` (fixed order: Gesamtbeurteilung, Projektfortschritt,
   Kosten, Personalaufwand, Projektrisiken): per row, `verdict_final = verdict_override ??
   verdict`, `reason_final = reason_override ?? reason`, `divergence = true` if either
   override is set, sourced from the operator's Prognose-Ampel-Override table.
5. Compute derived metrics (Step 5), including the two deferred Prognose-Ampel rows.
   Resolve story→spec links.

### Step 5 — Derived metrics

- **Personalaufwand (mechanical Prognose-Ampel row)** — once `kpis.gesamtfortschritt_pct`
  and `kpis.budgetverbrauch_pct` are final: `diff = gesamtfortschritt_pct -
  budgetverbrauch_pct`. `rot` if `diff < 0` (mehr Budget verbraucht als Fortschritt
  geliefert), `gelb` if `0 <= diff <= 10` (Budget und Fortschritt liegen knapp
  beieinander), else `gruen`. `reason` states the two numbers plainly, e.g. "Budgetverbrauch
  35% liegt deutlich unter Fortschritt 59%." No LLM judgment — this is a fixed formula so
  it stays stable across runs.
- **Gesamtbeurteilung (LLM synthesis, written last)** — one overall verdict + one honest
  sentence synthesizing Projektfortschritt, Kosten, Personalaufwand, and Projektrisiken.
  This is what drives `ampel.display` when the operator hasn't set an override in
  `status.md`'s `ampel` field.

- **Budget:** `budget_total_hours = budget_total_at × hours_per_at`;
  `ist_at = ist_stunden / hours_per_at`;
  `budgetverbrauch_pct = ist_at / budget_total_at × 100`.
- **Earned Value:** `earned_value_at = overall_progress_pct/100 × budget_total_at`;
  `variance_at = earned_value_at − ist_at` (negative = behind value). Note: `variance_at`
  is a cost/value-vs-effort (Kosteneffizienz) figure, NOT a schedule variance — schedule
  is expressed via the Prognose-Ampel and Fortschritt-vs-Zeit, not here.
- **KPIs:** Gesamtfortschritt %, Budgetverbrauch %, CI-Checks %,
  Tage bis Zieltermin (working days `report_date → target_date`).
- **CI trend & trajectory:** read prior `archive/report-data-*.json`, extract
  `(date_de, ci.pass_rate_pct)` and `(date_de, overall_progress_pct)` series, append the
  current run, de-dupe by date (latest of a day wins). Trajectory additionally merges the
  operator `## Verlauf` checkpoints from status.md — see "Trajectory" below.

### Step 6 — Render (deterministic script, do NOT hand-fill)

Rendering `report-data.json` + the template into `report.html` is pure mechanics —
run the renderer instead of substituting the template by hand (hand-filling wastes
tokens and risks miscomputed SVG geometry / dropped Umlaute):

```
python3 .claude/skills/project-report/render_report.py    # optional arg: reporting dir (default docs/reporting)
```

It reads `docs/reporting/report-data.json` + `template/report.html.tmpl`, writes a
self-contained `docs/reporting/report.html`, and **raises** if any `{{token}}` or
`<!-- REPEAT/IF/COMPUTE -->` marker is left unrendered (so a template change can't
silently produce a broken report). The renderer is stdlib-only Python 3, no deps.

The renderer owns the mustache-lite mini-language and the three SVG COMPUTE blocks
(budget bars, CI spark, trajectory). If you restructure the template — new sections,
renamed loop arrays, changed SVG viewBoxes — update `render_report.py` to match
(`LOOP_SINGULAR`, the `replace_between` anchors, the geometry helpers). The section
list & placeholders below document the contract the renderer implements.

If the template does not exist yet, tell the user the template task must run first;
still write `signals.json` and `report-data.json`.

### Step 7 — Write outputs + archive

Write `signals.json`, `report-data.json`, `report.html`, then copy the dated snapshots
`archive/report-YYYY-MM-DD.html` and `archive/report-data-YYYY-MM-DD.json` (overwrite if
the same day is re-run). Print a short German summary: Gesamtfortschritt, Ampel,
Budgetverbrauch, CI-Rate, and any degraded sources.

---

## status.md schema (operator-owned)

Front matter: `project_name`, `branch`, `target_date`, `stretch_date`,
`budget_total_at`, `hours_per_at`, `ampel` (`gruen`|`gelb`|`rot`|`gelb-rot`|""),
`ci_source` (`auto`|`manual`), `ci_tests_total`/`ci_tests_passed` (manual only),
`hours_columns` (optional `{person, week, hours, activity?}`), `hours_file` (optional
glob for the dated weekly hours export, newest match wins; defaults to `hours.xlsx`).

Body tables: **Lieferbereiche** (`id, name, weight, progress_override, status_override,
comment` — override columns blank by default), **Stories** (`id, title, area, progress
[0/25/50/75/100], status, next_proof, spec`), **Risiken**, **Scope-Cuts**, **Offene
Entscheidungen**, **Verlauf** (operator progress-history checkpoints, `Datum
(YYYY-MM-DD) | Fortschritt %` — the harness merges these with archived
`report-data.json` trajectory snapshots plus the current run, dedups by date, sorted
ascending; the current run's own point is added by the harness, not typed by the
operator), **Management Summary** (`summary_de` prose). Full column list in
`CONTRACT.md §1`.

## signals.json & report-data.json schemas

Defined in **`docs/reporting/CONTRACT.md` §2 and §3**. Do not diverge from them.

## Merge / override rules

Defined in **`CONTRACT.md`** (merge rules 1–6). Summary: override-or-estimate per area;
show both on divergence; overall = weighted sum of finals; operator ampel wins for
display but the 3-signal harness verdict is always shown too.

---

## CI extraction (gh check-runs) with manual fallback + graceful degradation

Progress is subjective; the CI-Checks pass rate is the one objective quality signal.

**Diagnosis for this repo:** the repo's tests DO run — on Jenkins, not GitHub Actions —
but Jenkins posts each job as a GitHub **check run** on the commit, and `gh` can read
those via the Checks API. So `ci_source: auto` WORKS, just not through GitHub Actions.
The signal is **JOB-level** (e.g. "unit tests", "robot tests" as named checks), not
individual test counts — per-test counts would require authenticated Jenkins access we
don't have.

1. If `ci_source: manual` → use `ci_tests_total` / `ci_tests_passed` from status.md.
   Set `ci.source = "manual"`, `note = "manual override"`. Skip gh.
2. Else (`auto`): resolve the branch's ORIGIN head sha — the local branch may be behind
   origin, so CI reflects origin's head; record the sha used:
   - `git ls-remote origin <branch>` → take the sha for that ref.
   - `gh api repos/4teamwork/opengever.core/commits/<sha>/check-runs --jq '.check_runs[] | {name, conclusion, url: .details_url}'`
   - Count conclusions: `checks_passed` = `conclusion == "success"`; `checks_failed` =
     `conclusion` in (`failure`, `timed_out`, `cancelled`, `action_required`).
     `checks_total = checks_passed + checks_failed` — neutral/skipped conclusions are
     EXCLUDED from the denominator; list any such checks separately if present (do not
     silently drop them from the record, just from the ratio).
   - `pass_rate_pct = round(checks_passed / checks_total * 100, 1)`. Record `commit`
     (short sha), `failing[]` (name + url of each non-passing job).
3. **Graceful degradation** — if `gh` is missing, unauthenticated, returns no checks, or
   the API call fails:
   - Fall back to `ci_tests_*`/manual counts if the operator provided them (even under
     `ci_source: auto`).
   - Otherwise set `ci.degraded = true`, leave counts `null`, and put the reason in
     `ci.note`. The report renders "CI-Checks: nicht verfügbar" — never a fabricated
     number.

## hours.xlsx ingestion + column mapping

The harness adapts to the export rather than dictating its format.

0. **Resolve the file.** Read `hours_file` from status.md front matter — a glob relative
   to `docs/reporting/` (e.g. `hintergrund-tasks-stunden-*.xlsx`). Glob it and pick the
   NEWEST matching file (by filename date if encoded, else mtime). If `hours_file` is
   unset, default to `docs/reporting/hours.xlsx`.
1. If no file resolves → `hours.present = false`; budget shows budget only, no Ist.
   Continue.
2. Read the first sheet. Identify three **logical** columns — person, week (or date),
   hours — plus optional activity/comment. Prefer the `hours_columns` mapping from
   status.md when the export headers differ; otherwise match on common German/English
   header names (Mitarbeiter/Person, Woche/KW/Datum, Stunden/Std/Hours).
3. If a column is a date, derive ISO week (`YYYY-Www`). Coerce hours to numbers
   (comma or dot decimals). Skip/So note unparseable rows.
4. Aggregate: `ist_stunden` (sum), `ist_at = ist_stunden / hours_per_at`, plus
   `by_person[]` and `by_week[]` series. Record `rows_parsed` and any mapping/parse notes
   in `hours.note`.

Use a small Python helper (`openpyxl`, available via `uv`) for parsing; keep it inline or
in the skill dir. Never hand the operator a required schema — map to their columns.

**General principle:** ingestion must be resilient to person/date embedded in a compound
label column; prefer an ISO date inside a label over a separate, unreliable date column.
Column headers alone are not trustworthy — inspect a sample of actual cell values before
trusting a header's declared meaning.

**Worked example — the real `hintergrund-tasks-stunden-*.xlsx` export.** Header row:
`Name`, `Datum`, `Geleistete Stunden`, `Verrechnete PT`, `Tagesanteil`, `Einsatztyp`,
`Taetigkeitsbeschreibung` (plus an unlabeled index column A). Quirks that must be handled:

- **Person AND date are embedded in the `Name` column**, formatted
  `"<Person> vom <YYYY-MM-DD>[ HH:MM]"` (e.g. `"Buchberger Thomas vom 2026-06-03"`).
  Extract `person` = text before `" vom "`; extract `date` = the `YYYY-MM-DD` token after
  `" vom "`.
- The separate `Datum` column is **UNRELIABLE** — it mixes mis-swapped datetimes and
  US-format strings. IGNORE it entirely; always take the date from the `Name` string.
- Hours = the `Geleistete Stunden` column. `Verrechnete PT` is the same value already
  divided by 8 — do NOT also sum it (would double-count).
- Derive ISO week (`YYYY-Www`) from the date extracted from `Name`, not from `Datum`.

---

## Render contract — section list & placeholders

Map the Swiss mockup components to these report sections. Each consumes fields from
`report-data.json` (paths relative to its root). German labels; mono English kicker.

**Masthead** (cover, not a numbered section) — `meta.project_name` (title),
`meta.report_date_de` (Stand), `ampel.display` (the red ● dot colour = traffic light),
`meta.branch`, Invert button. Kicker note: Branch wird nicht gemerged → Merges sind kein
Fortschrittssignal.

Numbered sections 01–10 are rendered as collapsible `<details class="section reveal">`
blocks. Each has a `<summary class="kicker">` (the clickable header) and a single
`<div class="section-body">` wrapping everything else — the JS collapse/expand animation
(Web Animations API, see the script block) targets that one wrapper, so any new section
MUST follow the same `<details class="section reveal" [open]><summary class="kicker">…
<span class="toggle-ind">+</span></summary><div class="section-body">…</div></details>`
shape or the animation has nothing to grab. 01–04 ship with the `open` attribute (default
expanded), 05–10 ship collapsed. If you add/remove/reorder a section, renumber
`section-no` sequentially and keep the open/collapsed split intentional — 01–04 are the
"state at a glance" sections a manager reads first, 05–10 are supporting detail. Collapse
animation respects `prefers-reduced-motion` (falls back to instant native toggle).

1. **Management Summary** — `summary_de` (operator bullets, plain Markdown; the renderer
   converts `- `/`**bold**` to `<ul><li>`/`<strong>` HTML inside a `<div>` at Step 6).
2. **KPI strip (4)** — `kpis.gesamtfortschritt_pct`, `kpis.budgetverbrauch_pct`
   (no absolute AT figures here — those live in the Budget section), KPI **"CI-Checks"**
   shown as "checks_passed/checks_total gruen" (e.g. "8/11 gruen", from
   `ci.checks_passed`/`ci.checks_total`; or "nicht verfügbar" when `ci.degraded`),
   `kpis.tage_bis_zieltermin`.
3. **Prognose-Ampel** — ledger table over `prognose.items[]` (fixed order:
   Gesamtbeurteilung, Projektfortschritt, Kosten, Personalaufwand, Projektrisiken),
   column header "Bereich"; each row's `verdict_final`/`reason_final` (override ??
   harness), with the harness `verdict`/`reason` shown as a footnote line when
   `divergence` is true. No separate operator/harness footer — the Gesamtbeurteilung
   row IS the operator-overridable overall call.
4. **Fortschritt nach Lieferbereich** — ledger table (no allocation-sum footer row —
   the KPI strip already carries `overall_progress_pct`) over `areas[]`: `name`,
   `weight`, `progress_final` (show `progress_estimate` + `progress_override` when
   `progress_divergence`, e.g. "Modell: 27 % · erfasst: 20 %"), `status_final`,
   `contribution_pct`, `comment`.
5. **Story-Burnup** — ledger over `stories[]`: `id`, `title`, `area`, `progress`
   (0/25/50/75/100), `status`, `next_proof`; link to `spec_path` where present
   (`spec_status` badge).
6. **Budget** — per-person/week bars from `budget.by_person`/`budget.by_week`; budget
   meter (`budget.budgetverbrauch_pct`); `budget.ist_at`, `budget.earned_value_at`,
   `budget.variance_at`. Render `variance_at` under the label **"Wert vs. Ist-Aufwand"**
   with caption/footnote **"Earned Value abzueglich verbuchtem Ist-Aufwand —
   Kosteneffizienz, keine Terminaussage."** — it is a cost-efficiency figure, not a
   schedule signal.
7. **CI-Qualitaet** — `ci.pass_rate_pct` (or degraded note), `ci.checks_passed`/
   `ci.checks_total`, `ci.commit`, a list of `ci.failing[]` (name + link), and
   `ci.trend[]` (using `date_de`) as a small line/spark over past runs.
8. **Offene Entscheidungen** — plain list over `offene_entscheidungen[]`. Its own section,
   placed just before Risiken. `scope_cuts[]` from status.md is intentionally NOT merged
   into `report-data.json` and has no section here — operator-only working notes (see
   CONTRACT.md §1).
9. **Risiken** — ledger over `risks[]`: Risiko, Kategorie, Auswirkung, Wahrscheinlichkeit,
   Fruehwarnsignal, Naechste Aktion, Owner, Status.
10. **Fortschritt** (Trajektorie) — actual progress-vs-time polyline drawn through
    `trajektorie.history[]` (using `date_de`), plus a dashed ideal line from
    `(trajektorie.ideal.start_date_de, 0 %)` to `(trajektorie.ideal.target_date_de,
    100 %)`, with a Zieltermin marker at `trajektorie.target_date_de` (and
    `stretch_date_de` if set). `history` is the harness merge of operator `## Verlauf`
    checkpoints + archived `report-data.json` snapshots + the current run, deduped by
    date and sorted ascending.

Reuse the mockup's ledger tables, KPI columns, alloc bar, data-ink SVG charts, tooltip,
count-up, and Invert theme toggle. Keep it one self-contained HTML file.
