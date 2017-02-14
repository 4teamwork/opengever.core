

## Abgrenzung / Gedanken

- **Sortierung Actions:** Die Sortierung der ``folder_buttons``-Actions ist
    nicht exakt gleich wie vorher, da nun die Dependencies
    (bspw. ``ftw.tabbedview``) vor og.core installiert werden.
    Da im ``actions.xml`` die Sortierung nicht gändert werden kann
    (``insert-after`` funktioniert nicht), ist dies schwierig zu korrigieren.
    Diese Änderung ist vernachlässigbar.
