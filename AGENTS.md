# Projektregeln

## Dokumentationsgrenze

Dieses Repository ist die maßgebliche Quelle für den projektspezifischen Code,
die Projektregeln, README, Architektur, Entscheidungen und den aktuellen Status.
Vor größeren Änderungen zuerst `AGENTS.md`, `README.md`, `PROJECT-STATE.md` und
relevante Dateien unter `docs\` lesen.

Homelab darf nur gezielt für allgemeines oder projektübergreifend
wiederverwendbares Hintergrundwissen durchsucht werden. Projektstatus,
Projekt-TODOs und konkrete Konfigurationen werden nicht dort geführt.

Vor Codeänderungen:

- `git status --short --branch` prüfen.
- Vorhandene uncommittete Änderungen respektieren; dokumentierte lokale Löschungen nicht eigenmächtig wiederherstellen.
- Keine fremden Änderungen überschreiben oder zurücksetzen.

Nach relevanten Änderungen prüfen, ob Status oder Projektdokumentation aktualisiert werden müssen.

Keine Secrets dokumentieren.

## Gemeinsamer Arbeitsablauf

Vor einer Aufgabe README, `PROJECT-STATE.md` und relevante `docs\` lesen;
Architektur respektieren und Änderungen klein halten. Vorhandene Tests nutzen
und nach relevanten Änderungen ausführen. Danach Status aktualisieren sowie
README oder `docs\` nur bei geändertem Verhalten oder Bedienung anpassen.
