# Multi-Agent Scaffolding System fuer Hochschulforschung (deutsche Version)

Ein modularer, experimentbereiter Prototyp eines Multi-Agenten-Scaffolding-Systems fuer Hochschulforschung. Das System nutzt eine hierarchische Architektur mit einem Lead-/Orchestrator-Agenten und spezialisierten Sub-Agenten, die jeweils ein eigenes Design Feature (DF) und eine zugeordnete Scaffolding-Art abbilden.

## Systemueberblick

Das Multi-Agent Scaffolding System (MAS) liefert scaffoldetes Feedback zu Concept Maps, um kontrollierte Experimente zur Wirksamkeit verschiedener Scaffolding-Mechanismen zu ermoeglichen. Das System:

- Ermoeglicht das Ein-/Ausschalten jedes Design Features per Konfiguration
- Unterstuetzt kontrollierbare, wiederholbare Interaktionsablaeufe fuer Experimente
- Bietet klare Logs, Modularitaet und Erweiterbarkeit
- Gibt keine direkten Antworten oder Loesungen – alles Feedback ist scaffoldet

## Architektur

```
                      ┌─────────────────┐
                      │   Lead Agent    │
                      │  (Orchestrator) │
                      └────────┬────────┘
                               │
                               │
            ┌──────────────────┼─────────────────┐
            │                  │                 │
┌───────────▼────────┐ ┌───────▼──────┐ ┌────────▼────────┐
│ Learner Profiling  │ │ Scaffolding  │ │   Example Map   │
│   Agent (DF1)      │ │Agents(DF1/2) │ │   Agent (DF3)   │
└────────────────────┘ └───────┬──────┘ └─────────────────┘
                               │
                             (DF2)
          ┌────────────────────┴─────────────────┐
          │                   │                  │
 ┌────────▼────────┐ ┌─────-──▼──────┐ ┌─────────▼────────┐
 │    Strategic    │ │  Conceptual   │ │  Metacognitive   │
 │   Scaffolding   │ │  Scaffolding  │ │   Scaffolding    │
 └─────────────────┘ └───────────────┘ └──────────────────┘
                                                 │
                                        ┌────────▼────────┐
                                        │   Procedural    │
                                        │ Scaffolding(DF4)│
                                        └─────────────────┘
```

### Rollen

1. **Lead Agent (Orchestrator)**
   - Steuert Workflow, Phasen, Nutzerprompts und Aktivierung der Sub-Agenten
   - Leitet Nutzereingaben an aktive Sub-Agenten weiter
   - Kombiniert Sub-Agenten-Ausgaben zu Nutzerfeedback
   - Erzwingt Reflexion/Antwort, bevor neue Vorschlaege kommen
   - Verwalten von Agenten-Lifecycle und Feature-Flags

2. **DF1: Learner Profiling & ZPD-Schaetzung**
   - Erfasst Vorwissen, Erfahrung und Ziele ueber Fragen
   - Analysiert Concept-Map-Einreichungen auf Vollstaendigkeit und Luecken
   - Schaetzt die Zone of Proximal Development (ZPD) des Lernenden
   - Liefert Scaffolding-Empfehlungen an den Orchestrator
   - Hae lt und aktualisiert Profil und ZPD-Schaetzung

3. **DF2: Spezialisierte Scaffolding-Subagenten**
   - **Strategic Scaffolding Agent**: Unterstuetzt Planung und Lernstrategien
   - **Conceptual Scaffolding Agent**: Hebt Konzepte/Beziehungen hervor, erkennt Luecken
   - **Metacognitive Scaffolding Agent**: Regt Planung, Monitoring, Selbststeuerung an
   - **Procedural Scaffolding Agent**: Fuehrt durch Tools/Interfaces und Schritte

4. **DF3: Example Map Agent (Ideal-Loesung)**
   - Haelt eine „Gold-Standard“-Concept Map zum Thema
   - Vergleicht Lernenden-Map mit Idealmap ohne diese offen zu legen
   - Gibt Feedback zu Abweichungen
   - Fordert immer zur eigenstaendigen Verbesserung auf

5. **DF4: Content Ingestion / Knowledge State**
   - Speichert laufend Concept Maps und hochgeladene Materialien
   - Stellt Kontext fuer andere Agenten bereit
   - Ermoeglicht zielgerichtetes Feedback durch Tracking von Aenderungen

## Experimentelle Bedingungen

### EG_SEQ (Treatment)
- **Agenten-Sequenz**: Conceptual → Procedural → Strategic → Metacognitive
- **Ziel**: Theoretisch optimale Scaffolding-Reihenfolge
- **Scaffolding**: Vollstaendig KI-gestuetzt, personalisiert
- **Erwartung**: Beste Lernzuwachse durch begruendete Sequenz

### CG_WRONG_SEQ (Control 1)
- **Agenten-Sequenz**: Metacognitive → Strategic → Procedural → Conceptual
- **Ziel**: Suboptimale Sequenz zum Vergleich
- **Scaffolding**: Gleiches Scaffolding, aber umgekehrte Reihenfolge
- **Erwartung**: Geringere Lernzuwachse

### CG_NEUTRAL (Control 2)
- **Agenten-Sequenz**: Neutral → Neutral → Neutral → Neutral
- **Ziel**: Keine Scaffolding-Kontrolle
- **Scaffolding**: Kontextbezogene Bestaetigungen ohne Lernunterstuetzung
- **Erwartung**: Basis-Lernzuwachs ohne Scaffolding

### Balancierte Zuweisung
- **Methode**: Deterministische Hash-Zuweisung per Session-ID
- **Verteilung**: Nahezu gleiche Teilnehmerzahl pro Bedingung
- **Persistenz**: Bedingung bleibt fuer alle Runden gleich
- **Logging**: Alle Interaktionen mit Bedingung getaggt

### NeutralAgent-Highlights
- Kontextbewusst (nutzt Concept Map)
- Kein Scaffolding, nur Bestaetigungen
- Gleiche Pattern-Filter wie Scaffolding-Agenten
- Fortschrittsfeedback vs. Expertenerwartung
- Natuerliche Antworten auf Fragen/Help-Seeking

## Forschungsziele

Das System ermoeglicht Studien zu:
- **Sequenz-Wirksamkeit**: Optimale vs. suboptimale Agenten-Reihenfolge
- **Scaffolding vs. kein Scaffolding**: Wirkung gegen neutrale Kontrolle
- **Agentenvergleich**: Welche Scaffolding-Art wirkt am staerksten?
- **Lernenden-Adaption**: Reaktion unterschiedlicher Profile
- **Concept-Map-Evolution**: Entwicklung unter verschiedenen Bedingungen
- **Gesprächsmuster**: Unterschiede zwischen Gruppen

## Neueste Updates (September 2025)

### Experimentelle Bedingungen
- Drei Bedingungen (EG_SEQ, CG_WRONG_SEQ, CG_NEUTRAL) mit balancierter Zuweisung
- Agenten-Sequenzen fest je Bedingung, Runde 0 baseline (kein Scaffolding)
- NeutralAgent als kontrollierter, kontextbewusster Nicht-Scaffolder

### Verbesserte Experimentalumgebung
- Feste Scaffolding-Sequenzen pro Bedingung
- Domänenspezifische Scaffolding-Konfigurationen
- Kopierschutz fuer Aufgabeninhalte
- Verbes serte Vorkenntnis-Abfrage
- Mehrere KI-Provider (OpenAI, Groq, Open Router) unterstuetzt

### Kernfeatures
- Balancierte Bedingungszuweisung
- Kontextbewusster Neutralagent
- Personalisiertes Profiling mit adaptiven Scaffolding-Leveln
- Multi-Turn-Dialoge (bis zu 5 Exchanges/Runde)
- Umfassendes Logging mit Bedingungs-Tags
- Interaktiver Concept-Map-Editor mit Live-Feedback
- Geschuetzte Aufgabenanzeige
- Erweitertes Pattern-Handling fuer natürliche Dialoge

## Installation

### Voraussetzungen
- Python 3.8 oder hoeher
- OpenAI API-Key (fuer Experimentalmodus)

### Setup
1. Repo klonen:
   ```bash
   git clone https://github.com/koizachek/scaffolding_multiagentsystem.git
   cd scaffolding_multiagentsystem
   ```
2. Abhaengigkeiten installieren:
   ```bash
   pip install -r MAS/requirements.txt
   ```
3. OpenAI-Key setzen:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   oder `.env` in `MAS/` mit:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Experimente ausfuehren

### Web-Interface starten
1. In das App-Verzeichnis:
   ```bash
   cd MAS/app
   ```
2. Streamlit starten:
   ```bash
   streamlit run app.py
   ```
3. Browser oeffnen (z. B. `http://localhost:8501`)

### Experimentablauf

1. **Moduswahl**
   - Experimental Mode: Echt-KI mit Logging (API-Key noetig)
   - Demo Mode: Statische Antworten (kein API-Key)
2. **Lernendenprofil (nur Experimental)**
   - Hintergrund, Vorwissen, Ziele
   - Selbstschaetzung Concept-Mapping
   - Automatische Scaffolding-Level-Zuweisung
3. **Funf Runden**
   - Runde 0: Baseline, keine Agenten
   - Runden 1–4: Agenten-Sequenz je Bedingung
   - Jeder Durchlauf: Map bauen → Agentenfeedback → bis zu 5 Dialogturns → Reflexion/Anpassung
4. **Datenexport**
   - JSON: `experimental_session_[name]_[timestamp].json`
   - Logs: `/MAS/app/logs/`, Forschungsfiles: `/MAS/experimental_data/`
   - MongoDB-Export moeglich

## Forschungsdaten & Logging

### Was geloggt wird
- Teilnehmerdaten: Profil, Vorkenntnis-Scores, Scaffolding-Level
- Interaktionen: Agenten-spezifische Historie, Dialoge, Concept-Map-Evolution, Zeiten/Engagement
- Performance: Komplexitaet (Nodes/Edges), Lernfortschritt, Scaffolding-Wirkung

### Beispiel Agenten-Logging
```json
{
  "conversation_history": {
    "round_0": [
      {
        "speaker": "conceptual_scaffolding",
        "agent_type": "conceptual_scaffolding",
        "message": "I notice your concept map focuses on...",
        "timestamp": "2025-08-02T19:04:57.758408"
      }
    ]
  }
}
```
- Analyse pro Agententyp
- Mustervergleich zwischen Agenten
- Tiefe der Gespraeche verfolgen

## Datenspeicherung
- **Experimental Data**: `MAS/experimental_data/` (JSON/CSV)
- **System Logs**: `MAS/app/logs/` (Technik/Errors)

## Interaktiver Concept-Map-Editor
- Visuelles Hinzufuegen von Konzepten
- Beziehungen mit Labels erstellen
- Echtzeit-Bearbeitung
- Kumulatives Bauen pro Runde
- Uebersicht (Node/Edge-Zahlen)

Workflow: Konzepte hinzufuegen → Verbindungen erstellen → Bearbeiten/loeschen → Einreichen.

## Verzeichnisstruktur (Kurz)
```
MAS/
├── app/ (Streamlit UI, Session-Logik, Komponenten)
├── config/ (Scaffolding-Templates, Domains)
├── agents/ (Scaffolding-Agenten, Factory)
├── utils/ (AI-API, Logging, Scaffolding-Utils)
├── examples/data/ (Expert-Map)
├── experimental_data/ (Forschungsdaten)
└── config.json (Systemkonfiguration)
```

## Konfiguration
Zentrale Datei: `MAS/config.json`
```json
{
  "max_rounds": 5,
  "agents": {
    "conceptual_scaffolding": {"enabled": true},
    "strategic_scaffolding": {"enabled": true},
    "metacognitive_scaffolding": {"enabled": true},
    "procedural_scaffolding": {"enabled": true}
  },
  "logging": {
    "log_dir": "logs",
    "log_level": "INFO"
  },
  "client": "openai",
  "primary_model": "gpt-4o",
  "fallback_model": "gpt-4o-mini"
}
```

### Domain-/Task-spezifisch
- Prompts pro Domain
- Angepasste Bewertungskriterien
- Custom-Expert-Konzepte
- Follow-up-Vorlagen

## Testen
```bash
cd /path/to/scaffolding_multiagentsystem
PYTHONPATH=. python MAS/test_imports.py
```
Prueft Importe, instanziiert das System, simuliert Scaffolding und zeigt Antworten.

## Forschungsanwendungen
- **Scaffolding-Effekt**: Agententyp-Vergleich
- **Lernendenmuster**: Engagement vs. Profile
- **Dialogtiefe**: Faktoren fuer tiefere Scaffolds
- **Lernergebnisse**: Map-Verbesserungen durch Scaffolding

## Troubleshooting
- **API-Key** setzen/exportieren
- **Port-Konflikt**: `streamlit run app.py --server.port 8502`
- **Daten fehlen**: Schreibrechte pruefen, Sessionabschluss, Logs sichten

Browser: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+, JS & Local Storage aktiviert.

## Abhaengigkeiten
Kern (siehe `MAS/requirements.txt`): `streamlit`, `openai`, `pandas`, `json`, `datetime`.

## Mitwirken
- Neue Agenten in `MAS/agents/`
- Agentenverhalten anpassen in den Agentenfiles
- UI erweitern in `MAS/app/`
- Logging-Metriken in `MAS/utils/logging_utils.py`

## Lizenz
Entwickelt fuer Hochschulforschung zu Scaffolding-Mechanismen.

## Danksagung
Forschungsprototyp zur Untersuchung von Multi-Agent-Scaffolding in Bildungsszenarien.
