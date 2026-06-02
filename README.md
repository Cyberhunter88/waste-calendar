# Zweibruecken Waste Calendar

Home-Assistant-Custom-Integration fuer den UBZ-Abfallkalender in Zweibruecken.
Die Integration liest eine ICS/iCal-URL und erstellt Sensoren fuer die naechsten
Abholtermine.

## Funktionen

- Einrichtung ueber die Home-Assistant-UI
- Installation ueber HACS als benutzerdefiniertes Repository
- Sensoren fuer `Bioabfall`, `Papier`, `Gelbe Tonne` und `Restmuell`
- Attribute fuer Tage bis zur Abholung, Heute/Morgen-Status, Originaltermin und Quelle
- Keine PDF-Auswertung und kein Web-Scraping, nur der ICS/iCal-Export

## HACS Installation

1. Dieses Repository zu GitHub hochladen.
2. In Home Assistant HACS oeffnen.
3. Rechts oben auf die drei Punkte klicken und `Benutzerdefinierte Repositories` waehlen.
4. Die GitHub-Repository-URL einfuegen.
5. Als Kategorie `Integration` auswaehlen.
6. `Zweibruecken Waste Calendar` installieren.
7. Home Assistant neu starten.
8. Unter `Einstellungen > Geraete & Dienste > Integration hinzufuegen` nach `Zweibruecken Waste Calendar` suchen.

## Konfiguration

1. Den UBZ-Abfallkalender oeffnen:
   <https://www.ubzzw.com/servicebereiche/abfall/abfallkalender/>
2. Strasse und Hausnummer auswaehlen.
3. Die Termine als ICS/iCal-Kalender exportieren.
4. Die ICS/iCal-URL in der Integration eintragen.

Optional kann das Aktualisierungsintervall angepasst werden. Standard ist alle
12 Stunden.

## Erstellte Sensoren

Die Integration legt vier Datumssensoren an:

- `sensor.bioabfall`
- `sensor.papier`
- `sensor.gelbe_tonne`
- `sensor.restmuell`

Jeder Sensor zeigt als Status das naechste bekannte Abholdatum. Zusaetzlich
werden diese Attribute gesetzt:

- `days_until`
- `is_today`
- `is_tomorrow`
- `next_collection`
- `summary`
- `waste_type`
- `source`

## Beispiel Dashboard-Karten

```yaml
type: grid
cards:
  - type: tile
    entity: sensor.bioabfall
  - type: tile
    entity: sensor.papier
  - type: tile
    entity: sensor.gelbe_tonne
  - type: tile
    entity: sensor.restmuell
```

## Beispiel Automation

```yaml
alias: Muell morgen rausstellen
trigger:
  - platform: time
    at: "18:00:00"
condition:
  - condition: template
    value_template: >
      {{ state_attr('sensor.restmuell', 'is_tomorrow')
         or state_attr('sensor.bioabfall', 'is_tomorrow')
         or state_attr('sensor.papier', 'is_tomorrow')
         or state_attr('sensor.gelbe_tonne', 'is_tomorrow') }}
action:
  - service: notify.mobile_app_dein_handy
    data:
      title: Muell
      message: Morgen ist eine Abholung geplant.
```

## Unterstuetzte Terminbezeichnungen

Der Parser erkennt typische deutsche Termintexte, unter anderem:

- `Biotonne`, `Bio`, `Bioabfall`
- `Papiertonne`, `Papier`, `Altpapier`
- `Gelbe Tonne`, `Gelber Sack`, `Gelb`
- `Restabfall`, `Restmuell`, `Schwarze Tonne`

Falls UBZ die Bezeichnungen im Kalender aendert, koennen neue Suchbegriffe in
`custom_components/zweibruecken_waste/const.py` ergaenzt werden.

## Entwicklung

```powershell
pytest
```

## Repository-Struktur

```text
custom_components/
  zweibruecken_waste/
    __init__.py
    calendar.py
    config_flow.py
    const.py
    coordinator.py
    manifest.json
    sensor.py
    strings.json
hacs.json
README.md
```

## Lizenz

Bitte vor der Veroeffentlichung eine passende Lizenzdatei ergaenzen, falls das
Repository oeffentlich geteilt werden soll.
