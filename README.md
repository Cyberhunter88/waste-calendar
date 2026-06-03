# Waste Calendar

Home-Assistant-Custom-Integration fuer den UBZ-Abfallkalender in Zweibruecken.
Die Integration liest eine ICS/iCal-URL und erstellt Sensoren fuer die naechsten
Abholtermine.

## Funktionen

- Einrichtung ueber die Home-Assistant-UI
- Installation ueber HACS als benutzerdefiniertes Repository
- Sensoren fuer `Bioabfall`, `Papier`, `Gelbe Tonne` und `Restmuell`
- Optionaler Home-Assistant-Kalender mit den kommenden Abfallterminen
- Attribute fuer Tage bis zur Abholung, Heute/Morgen-Status, Originaltermin und Quelle
- Keine PDF-Auswertung und kein Web-Scraping, nur der ICS/iCal-Export

## Installation

### HACS (empfohlen)

[![Open your Home Assistant instance and open a repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Cyberhunter88&repository=waste-calendar&category=integration)

<details>
<summary>Alternative zum Button</summary>

1. In Home Assistant HACS oeffnen.
2. Rechts oben auf die drei Punkte klicken und `Benutzerdefinierte Repositories` waehlen.
3. Die GitHub-Repository-URL einfuegen:
   `https://github.com/Cyberhunter88/waste-calendar`
4. Als Kategorie `Integration` auswaehlen.
5. `Waste Calendar` installieren.
6. Home Assistant neu starten.
7. Unter `Einstellungen > Geraete & Dienste > Integration hinzufuegen` nach `Waste Calendar` suchen.

</details>

### Manuelle Installation

<details>
<summary>Manuelle Installationsschritte</summary>

1. Dieses Repository herunterladen.
2. Den Ordner `custom_components/zweibruecken_waste` in den `custom_components`-Ordner der Home-Assistant-Installation kopieren.
3. Home Assistant neu starten.
4. Unter `Einstellungen > Geraete & Dienste > Integration hinzufuegen` nach `Waste Calendar` suchen.

</details>

## Voraussetzungen

- Home Assistant mit Zugriff auf den Ordner `custom_components`
- Eine ICS/iCal-URL aus dem UBZ-Abfallkalender

## Konfiguration

1. Den UBZ-Abfallkalender oeffnen:
   <https://www.ubzzw.com/servicebereiche/abfall/abfallkalender/>
2. Strasse und Hausnummer auswaehlen.
3. Beim Ergebnis den Link `Diese Leerungstermine in einer ical-Kalenderdatei`
   mit der rechten Maustaste anklicken.
4. `Link-Adresse kopieren` waehlen. Nicht die heruntergeladene `.ics`-Datei
   selbst auswaehlen.
5. Die kopierte Adresse in der Integration eintragen.

Hinweis: Manche Browser kopieren Kalenderlinks als `webcal://...`. Die
Integration wandelt diese Adresse automatisch in `https://...` um.

Falls sich der Link nicht kopieren laesst:

1. Den Link `Diese Leerungstermine in einer ical-Kalenderdatei` anklicken.
2. Die heruntergeladene `.ics`-Datei mit einem Texteditor oeffnen.
3. Den kompletten Inhalt markieren und kopieren.
4. Diesen Inhalt in das Feld `ICS/iCal-URL oder Dateiinhalt` einfuegen.

Optional kann das Aktualisierungsintervall angepasst werden. Standard ist alle
12 Stunden.

Optional kann beim Einrichten oder spaeter in den Integrationsoptionen ein
Home-Assistant-Kalender aktiviert werden. Dieser Kalender zeigt die passenden
Abfalltermine aus der ICS-Datei als ganztägige Termine an.

## Erstellte Sensoren

Die Integration legt vier Sensoren an:

- `sensor.bioabfall`
- `sensor.papier`
- `sensor.gelbe_tonne`
- `sensor.restmuell`
- `calendar.abfalltermine`, wenn die Kalenderoption aktiviert ist

Jeder Sensor zeigt als Status das naechste bekannte Abholdatum im deutschen
Format, zum Beispiel `17.06.2026`. Wenn die Abholung heute oder am naechsten
Tag stattfindet, zeigt der Status `Heute` oder `Morgen`. Zusaetzlich werden
diese Attribute gesetzt:

- `days_until`
- `is_today`
- `is_tomorrow`
- `next_collection` als technisches ISO-Datum, zum Beispiel `2026-06-17`
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
