_PR-Beschreibung: muss alle notwendigen Informationen enthalten, so dass ein Aussenstehender die Änderung versteht ohne den Code oder den Issue anzuschauen!_

- _Grund, wieso diese Änderung notwendig ist_
- _Was das Ziel dieser Änderung ist_
- _Wie die Änderung erreicht wird (z.B. Design-Entscheide)_
- _Der Autor soll im PR Body die Änderung anpreisen und verkaufen_

_Screenshot: erwünscht, sollen aber immer nur unterstützend eingesetzt werden._


Definition of Done: https://4teamwork.atlassian.net/wiki/spaces/CHX4TW/pages/917562/


## Checkliste (Must have)

_Alles muss gemacht/angehakt werden._

- [ ] Changelog-Eintrag erstellt? _Falls im PR nicht vorhanden erachtet es der PR-Ersteller als unnötig._
- [ ] Aktualisierung Dokumentation (API/Deployment/...) aktualisiert? _Falls im PR nicht vorhanden erachtet es der PR-Ersteller als unnötig._
- [ ] Jira Link + Backlink im Jira / Github Issue Link. _Link muss im PR-Body vorhanden sein._


## Checkliste (optional)

_Nur Zutreffendes soll angehakt stehengelassen werden._

- [ ] Gibt es neue Funktionalität mit einem `Dokument`? Funktioniert das auch mit einem `Mail`?
- [ ] Wurde etwas an der `Aufgabe` angepasst? Funktioniert das auch mit einer `Weiterleitung`?
- [ ] Profil angepasst? Sind UpgradeSteps vorhanden/nötig?:
- [ ] Sind UpgradeSteps `deferrable`, oder können gewisse Schritte des Upgrades konditional ausgeführt werden?
- [ ] Gibts es eine DB-Schema Migration?
  - [ ] Wurde alle Columns/Änderungen aus dem Modell in einer DB-Schema Migration nachgeführt.
  - [ ] Sind Constraint-Namen maximal 30 Zeichen lang (`Oracle`)?
- [ ] Gibt es ein neues Feature-Flag? Wurden dafür Tests mit aktiviertem und deaktivierte Flag geschrieben?
- [ ] Könnten Kundeninstallationen von den Änderungen betroffen sein? Müssen Policies angepasst werden?
- [ ] Gibt es neue Übersetzungen?
  - [ ] Sind alle msg-Strings in Übersetzungen Unicode?
  - [ ] Wird die richtige i18n-domain verwendet (Copy-Paste Fehler sind hier häufig)?
- [ ] Wenn bei Schema-definitionen `missing_value` spezifiziert ist muss immer auch `default` auf den gleichen Wert gesetzt werden
