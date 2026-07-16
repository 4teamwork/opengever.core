---
# ═══════════════════════════════════════════════════════════════════════════
# OPERATOR-EBENE — Diese Datei bearbeitet NUR der Mensch (Projektleitung).
# Die Harness (Skill /report) LIEST diese Datei und schreibt hier NIE hinein.
# Maschinelle Signale stehen getrennt in signals.json (die bearbeitet der Mensch NIE).
# Jedes Feld hat genau EINEN Schreiber. Trennung nach Schreiber ist das ganze Prinzip.
# Sprache: Deutsch, Schweizer Konvention — echte Umlaute ä/ö/ü verwenden, aber KEIN ß —
# immer "ss".
# Schema-Referenz: docs/reporting/CONTRACT.md §1
# ═══════════════════════════════════════════════════════════════════════════

project_name: "Hintergrundtasks"   # Projektname im Masthead
branch: "ai-playground"            # Explorativer Langzeit-Branch. Wird NICHT gemerged
                                   # -> gemergte PRs sind KEIN Fortschrittssignal.

# — Termine (YYYY-MM-DD) —
target_date: "2026-08-31"          # Zieltermin (fix). Scope-Cuts sind das Hauptsteuerungsmittel.
stretch_date: "2026-09-14"         # Streckungsende (1-2 Wochen Reserve). Leer = keine Streckung.

# — Budget —
budget_total_at: 49                # Gesamtbudget in Arbeitstagen (AT). Vorgabe Projektleitung.
hours_per_at: 8                    # Stunden pro Arbeitstag (Default 8).

# — Management-Ampel (Operator-Entscheid) —
# Bewusste Management-Einschätzung: gruen | gelb | rot | gelb-rot | "" (leer = nur Harness-Signal).
# Der Report zeigt DANEBEN immer die 3-Signal-Prognose der Harness. Beide bleiben getrennt.
ampel: "gruen"

# — CI-Checks (die eine objektive Qualitätskennzahl) —
# ci_source: auto   -> Harness liest die GitHub-Check-Runs (von Jenkins gepostet) auf dem
#                       origin-Head-Commit von {branch} ab (checks_passed/checks_total).
# ci_source: manual -> Harness nutzt die zwei Felder unten (Fallback bei gh nicht verfügbar/uneindeutig).
# Die Tests laufen auf Jenkins, nicht auf GitHub Actions -- Jenkins postet jeden Job aber
# als Check-Run auf den Commit, und `gh` kann diese über die Checks-API lesen. ci_source:
# auto funktioniert daher. Das Signal ist auf Job-Ebene (benannte Checks), nicht auf
# Test-Ebene -- Einzel-Testzahlen würden authentifizierten Jenkins-Zugriff erfordern, den
# wir nicht haben. Ohne verfügbare Checks bleibt die CI-Kennzahl "nicht verfügbar" (kein
# erfundener Wert).
ci_source: "auto"
# ci_tests_total: 0                # nur bei ci_source: manual
# ci_tests_passed: 0               # nur bei ci_source: manual

# — hours.xlsx Spalten-Mapping (optional) —
# Nur setzen, wenn die Kopfzeilen des Zeit-Exports abweichen.
# Logische Spalten: person, week (oder date), hours (+ optional activity).
# hours_columns: { person: "Mitarbeiter", week: "Woche", hours: "Stunden", activity: "Tätigkeit" }

# — hours-Datei (Glob, neueste Datei gewinnt) —
# Der wochentliche Export ist datiert, z.B. hintergrund-tasks-stunden-260708.xlsx.
# Die Harness sucht in docs/reporting/ nach diesem Glob und nimmt die NEUESTE Fundstelle.
# Nicht gesetzt = Fallback auf hours.xlsx.
hours_file: "hintergrund-tasks-stunden-*.xlsx"
---

<!-- ═══════════════════════════════════════════════════════════════════════
     Operator-eigene Inhalte. Stand nach Durchsicht des Branch-Codes (ai-playground,
     HEAD d96de2b): Das Framework, der Kill-Switch/Dispatcher und alle drei geplanten
     Operationen (Berechtigungen setzen, Ordnungssystem-Metadaten, Dossiers verschieben)
     sind implementiert und mit Tests belegt. Der Stand liegt deutlich über der frühen
     Einschätzung "16%".
     ═══════════════════════════════════════════════════════════════════════ -->

## Lieferbereiche

<!-- Gewichte sind operator-eigen (Summe = 100). Die Override-Spalten sind standardmässig LEER:
     dann gewinnt die Harness-Schätzung (progress_estimate / status_signal) aus signals.json.
     Nur ausfüllen, um die Harness bewusst zu überstimmen. Divergenz zeigt der Report doppelt.
     Spalten: id | Name | Gewicht % | Fortschritt-Override % | Status-Override | Kommentar -->

| Bereich | Name | Gewicht % | Fortschritt-Override % | Status-Override | Kommentar |
|---|---|---:|---:|---|---|
| D0 | Solution Design & Spec-Backlog | 10 |  |  | 6 Specs abgeschlossen; Scope geklärt; Sync/Async über Kill-Switch gelöst |
| D1 | Framework + Operation 1 "Berechtigungen setzen" | 30 |  |  | Framework + Operation 1 produktiv. Offen: Objekt-Sperre, Benachrichtigung |
| D2 | UI-Transparenz & Admin-Übersicht | 15 |  |  | Nicht gestartet; kein Code |
| D3 | Operation "Metadaten Ordnungssystem anpassen" | 15 |  |  | Beide Operationen implementiert & getestet; Abnahmetests offen |
| D4 | Operation "Dossiers innerhalb Mandant verschieben" | 20 |  |  | Geliefert (höchstes Risiko); Sonderfälle noch auszubauen |
| D5 | Hardening, Performance & Abnahme | 10 |  |  | Kill-Switch + Tests vorhanden; E2E, Lasttest, Doku, Abnahme offen |

## Stories

<!-- Operative Wochensicht. Fortschritt bewusst grob in 0/25/50/75/100, damit die Pflege klein bleibt.
     "spec" verlinkt optional auf ein BMAD-Spec-File in _bmad-output/ (die Harness löst den Status auf).
     Spalten: id | Thema | Bereich | Fortschritt % | Status | Nächster Nachweis | spec -->

| ID | Thema | Bereich | Fortschritt % | Status | Nächster Nachweis | Spec |
|---|---|---|---:|---|---|---|
| S01 | Solution Design Hintergrund-Task-Framework | D0 | 100 | gruen | Abgeschlossen | spec-background-tasks-infrastructure.md |
| S02 | Sync/Async-Verhalten definieren | D0 | 75 | gruen | Entschieden: globaler Kill-Switch + synchroner Fallback; Schwellwerte pro Operation bei Bedarf nachziehen | spec-background-tasks-kill-switch.md |
| S03 | Scope-Schärfung der Operationen | D0 | 100 | gruen | Alle drei Operationen als Spec + Code umgesetzt | |
| S04 | Spec- & Akzeptanz-Template + priorisiertes Backlog | D0 | 100 | gruen | Sechs Specs nach Template erstellt | |
| S05 | Persistente Task-Warteschlange & Datenmodell | D1 | 100 | gruen | Modell + Upgrade-Step für Tabelle vorhanden | spec-background-tasks-infrastructure.md |
| S06 | Task-Lebenszyklus & Statusmaschine | D1 | 100 | gruen | pending/running/succeeded/failed + Reset unterbrochener Tasks getestet | spec-background-tasks-infrastructure.md |
| S07 | Sequenzieller Worker | D1 | 100 | gruen | run_forever/claim_next_task + Worker-Tests vorhanden | spec-background-tasks-infrastructure.md |
| S08 | Single-Flight / Run-Lock | D1 | 50 | gelb | Ein Worker pro Admin-Unit angenommen; expliziter Lock gegen Mehrfach-Worker offen | spec-background-tasks-infrastructure.md |
| S09 | Konfliktrobuste, wiederaufnehmbare Verarbeitung | D1 | 75 | gruen | Checkpointing/Retries/Reset vorhanden; unter Last an echter Operation nachweisen | spec-background-tasks-infrastructure.md |
| S10 | Objekt-Sperre während aktivem Task | D1 | 25 | rot | Bewusst zurückgestellt; Dedup storniert nur PENDING, keine echte Sperre | spec-background-tasks-infrastructure.md |
| S11 | Dispatcher sync/async | D1 | 100 | gruen | queue_task + synchroner Fallback bei deaktiviertem Feature | spec-background-tasks-kill-switch.md |
| S12 | Benachrichtigung bei Abschluss/Fehler | D1 | 0 | rot | Nur Sentry/Logging; Anbindung ans Activity-/Benachrichtigungssystem fehlt | |
| S13 | Operation 1 "Berechtigungen setzen" | D1 | 100 | gruen | reindexObjectSecurity produktiv gepatcht, Enqueue-Worker-Execute + Dedup belegt | spec-reindex-object-security-background-task.md |
| S14 | Kill-Switch / Notbremse (Registry + Upgrade) | D5 | 100 | gruen | Feature-Flag mit Fail-Safe (deaktiviert = synchron) + Upgrade-Step | spec-background-tasks-kill-switch.md |
| S15-S18 | UI-Indikator, UI-Sperre, Admin-Übersicht, Logs | D2 | 0 | grau | Start nach Stabilisierung; kein Code vorhanden | |
| S19 | Operation "Referenz-Präfixe aktualisieren" (Ordnungssystem) | D3 | 100 | gruen | update-reference-prefixes-Task + Subscriber angebunden, getestet | spec-update-reference-prefixes-background-task.md |
| S20 | Operation "Dossier-Titel reindexieren" | D3 | 100 | gruen | reindex-dossier-title-Task + Handler getestet | spec-reindex-dossier-title-background-task.md |
| S21 | Konsistenz-/Abnahmetests Ordnungssystem-Operation | D3 | 25 | gelb | Ende-zu-Ende-Nachweis der Solr-Mutation unter Last | |
| S22 | Operation "Dossiers/Objekte verschieben" | D4 | 100 | gruen | move-objects-Task + Anbindung in move_items; 208-Zeilen-Testsuite | spec-move-objects-background-task.md |
| S23 | Konsistenztests Verschieben (Berechtigungen, Sperren, Sonderfälle) | D4 | 40 | gelb | Sonderfälle (gesperrte/ausgecheckte Objekte, fehlende Rechte) vollständig abdecken | |
| S24-S26 | E2E, Lasttest, Doku, Release-Vorbereitung | D5 | 0 | grau | Am Ende, aber nicht komplett kürzbar | |

## Prognose-Ampel-Override

<!-- Die Harness generiert Verdict + Begründung für jede Zeile der Prognose-Ampel (fünf
     Bereiche, siehe unten) und schreibt sie nach signals.json. Die Override-Spalten hier
     sind standardmässig LEER: dann gewinnt die Harness. Nur ausfüllen, um bewusst zu
     überstimmen; der Report zeigt dann beides (Zeile + "Harness: …"-Fussnote).
     Bereich ist ein fester Schlüssel (nicht umbenennen): gesamtbeurteilung |
     projektfortschritt | kosten | personalaufwand | projektrisiken.
     Spalten: Bereich | Verdict-Override | Begründung-Override -->

| Bereich | Verdict-Override | Begründung-Override |
|---|---|---|
| gesamtbeurteilung |  |  |
| projektfortschritt |  |  |
| kosten |  |  |
| personalaufwand |  |  |
| projektrisiken |  |  |

## Risiken

<!-- Jede Woche 10 Minuten: neue Unsicherheiten sichtbar machen, bevor sie Termin/Budget treffen.
     Spalten: Risiko | Kategorie | Auswirkung | Wahrscheinlichkeit | Frühwarnsignal | Nächste Aktion | Owner | Status -->

| Risiko / Unsicherheit | Kategorie | Auswirkung | Wahrscheinlichkeit | Frühwarnsignal | Nächste Aktion | Owner | Status |
|---|---|---|---|---|---|---|---|
| Drei CI-Checks rot (test-solr, test-i18n-de, test-plone-4.3.x) | Qualität | Regressionen bleiben unentdeckt, Abnahme verzögert | Hoch | Rote Checks auf origin-Head | Ursachen je Check analysieren und grün stellen | Entwickler | Offen |
| Benutzerbenachrichtigung fehlt | Funktion | Anwender erfährt Abschluss/Fehler eines Tasks nicht | Hoch | Task schlägt still fehl, nur im Log sichtbar | Anbindung ans Activity-System umsetzen | Entwickler | Offen |
| Objekt-Sperre während aktivem Task offen | Technik | Inkonsistente Daten bei parallelen Änderungen | Mittel | Doppelte/kollidierende Tasks auf demselben Objekt | Minimalstrategie definieren und testen | Entwickler | Offen |
| Silent-Fail bei fehlendem Worker / abgebrochener Transaktion | Technik | Reindex/Verschiebung geht ohne Fehler verloren | Mittel | Deferred-Work-Punkte (Transaction abort, kein Worker) | After-Commit-Hook / Fallback-Logging prüfen | Entwickler | Beobachten |
| UI-Transparenz (D2) noch nicht gestartet | Termin/Scope | Kein Einblick in Task-Status für Anwender/Support | Mittel | D2 startet erst spät | Minimal-Admin-Übersicht früh einplanen | PL | Offen |
| Abnahme/Hardening (D5) offen | Termin | E2E-, Last- und Abnahmenachweis fehlt am Ende | Mittel | Kein E2E-/Lasttest bis KW32 | D5-Scope früh festlegen | PL | Beobachten |
| Ferien / Verfügbarkeit | Organisation | Review- und Entscheidungsverzug | Mittel | Antwortzeiten > 2 Arbeitstage | Abwesenheiten im Dashboard ergänzen | PL | Offen |


## Offene Entscheidungen

<!-- Freie Liste offener Entscheide, die Fortschritt oder Scope blockieren. -->

- Objekt-Sperre während aktivem Task: Minimalstrategie definieren (aktuell nur PENDING-Dedup)
- Benutzerbenachrichtigung: Umfang (nur Fehler vs. Abschluss+Fehler) und Anbindung ans Activity-System
- Minimalumfang der Admin-Übersicht (D2) festlegen
- Ob Sync/Async-Schwellwerte pro Operation zusätzlich zum globalen Kill-Switch nötig sind
- Umgang mit stillem Verlust bei abgebrochener Transaktion / fehlendem Worker (After-Commit-Hook?)

## Verlauf

<!-- Operator-bekannte Fortschritts-Meilensteine (Projektstart, frühere Dashboard-Stände etc.).
     Die Harness MERGT diese Checkpoints mit archivierten report-data.json-Trajektorie-Ständen
     und dem aktuellen Lauf, dedupliziert nach Datum, aufsteigend sortiert. Der Punkt des
     aktuellen Laufs wird von der Harness ergänzt, nicht hier eingetragen.
     Spalten: Datum (YYYY-MM-DD) | Fortschritt % -->

| Datum (YYYY-MM-DD) | Fortschritt % |
|---|---:|
| 2026-06-12 | 0 |
| 2026-06-19 | 13 |
| 2026-06-26 | 16 |
| 2026-07-03 | 23 |

## Management Summary

<!-- Operator-Prosa (summary_de) für einen Manager, der den Stand in 15 Sekunden erfassen
     muss: Fortschritt, Termin, Budget, Risiko, Ampel-Empfehlung. Kurze Bullet-Punkte statt
     Fliesstext, fett nur das Stichwort/die Zahl, kein Fülltext. Normale Markdown-Liste
     ("- " + **fett**) — der Renderer (render_report.py) wandelt das beim Bauen von
     report.html in HTML um; hier bleibt es reines Markdown (siehe CONTRACT.md §1).
     Dies ist der EINZIGE Ort für die narrative Einschätzung. Die Harness schreibt hier nichts. -->

- **Fortschritt:** 59% gewichtet — deutlich vor Plan (34% der Zeit verstrichen).
- **Kernnutzen geliefert:** Alle drei Operationen (Berechtigungen, Ordnungssystem-Metadaten, Verschieben) umgesetzt.
- **Budget:** 35% verbraucht (17.3 von 49 AT); erarbeiteter Wert übersteigt Ist-Aufwand — kosteneffizient.
- **Offen:** Benutzerbenachrichtigung, Objekt-Sperre, Admin-Übersicht (D2), Abnahme/Hardening (D5).
- **Ampel-Empfehlung:** Grün — vor Plan, Restarbeit bekannt und begrenzt.
</content>
