## Funktionsweise

1. `opengever.core` auf neuestem `master` auschecken oder aktualisieren.
2. ``git clone git@github.com:4teamwork/opengever.core.git src/profile-merge-tool --branch=jone-profile-merge-tool --single-branch``.
3. Plone Site löschen, neue, leere Development-Site aufsetzen.
4. Konfiguration dumpen
   - ``./bin/instance run src/profile-merge-tool/dump-gs-profile.py before``
5. Migration durchführen
   - ``./bin/zopepy ./src/profile-merge-tool/merge.py``
6. ``bin/test`` sollte jetzt alles grün sein.
7. Plone Site löschen, neue, leere Development-Site aufsetzen
8. Konfiguration dumpen
   - ``./bin/instance run src/profile-merge-tool/dump-gs-profile.py after``
9. Konfigurationen diffen
   - ``./bin/zopepy src/profile-merge-tool/dump-differ.py src/profile-merge-tool/dumps/before src/profile-merge-tool/dumps/after``
   - Abgleichen mit "Erwartete Veränderungen am GS Profile" (siehe unten)



## Erwartete Veränderungen am GS Profile

- Die Actions sind z.T. anders sortiert, da wir die Dependencies (ftw.*) nun
  *vor* den GEVER-Komponenten installieren, und nicht mehr *während*. Dies
  betrifft glücklicherweise nur Actions, deren Sortierung nicht relevant ist:
    - ``folder_buttons:reset_tableconfiguration``
    - ``folder_buttons:zip_selected``
    - ``folder_buttons:create_disposition``
    - ``object_buttons:zipexport``
- ``types.xml``: andere Reihenfolge, dies ist aber irrelevant (factories menu
  wird immer noch nachsortiert).
- Viewlets: Es sind nicht mehr alle alten Skins gleich registriert wegen
  veränderter Installationsreihenfolge. Ist aus meiner Sicht ok.


## Entscheide

- **Sortierung Actions:** Die Sortierung der ``folder_buttons``-Actions ist
    nicht exakt gleich wie vorher, da nun die Dependencies
    (bspw. ``ftw.tabbedview``) vor og.core installiert werden.
    Da im ``actions.xml`` die Sortierung nicht gändert werden kann
    (``insert-after`` funktioniert nicht), ist dies schwierig zu korrigieren.
    Diese Änderung ist vernachlässigbar.

- **XML Auto-Indent:** Die XML-Dateien (zcml, GS), die bearbeitet werden
    mussten, wurden mit lxml manipuliert. Da lxml aber die Attribute auf eine
    Zeile schreibt, war das Ergebnis z.T. unschön.
    Daher werden bei der Migration alle manipulierten XMLs gleich noch "pretty"
    gemacht, nach eigenen Einstellungen.

- **Policy konfiguration:** Die Policy hat neu keine Dependency auf
    ``opengever.polciy.base:default`` mehr, aber auch nicht auf
    ``opengever.core:default`` (dies würde zu 2 imports führen).
    Jedoch wird eine soft-dependency für ``ftw.upgrade`` deklariert (in der
    ``upgrade-step:directory`` Direktive).

- **Verhindern von GS imports:** Es wird per subscriber verhindert, dass ein
    altes Profile (z.b. ``opengever.task:default``) installiert wird. Dies ist
    nicht mehr sinnvoll. Des weiteren wird verhindert, dass ``opengever.` und
    ``ftw.`` profile zweimal importiert werden.

- **Testing: portal_languages:** Vorher wurde das ``portal_languages.xml`` im
    testing nicht importiert, da ``opengever.policy.base:default`` nie im test
    importiert wurde.
    Da das ``portal_languages.xml`` neu im ``opengever.core:default``-Profil
    ist, wird dies importiert. Im testing wird die Sprache auf Englisch
    zurückgestellt damit die Tests weiterhin unverändert passen.

- **Testing: filter_content_types:** Im Test wird auf dem ``Plone Site``-FTI
    ``filter_content_types``auf ``False`` gesetzt, da sich noch viele Tests
    darauf verlassen.

- **Tests: ZIP-Export:** Im ``registry.xml`` werden die Zip-Unterstützenden
    Interfacs konfiguriert. Vorher wurde dies im Test nicht gemacht.
    Einige Tests mussten korrigiert werden und die ZIP-Action entfernt.

- **Tests: Sortierung:** Da gewisse Actions und FTI anders sortiert sind mussten
    einige Tests angepasst werden, so dass diese die Sortierung nicht mehr
    testen sondern nur den Inhalt von Listen.
