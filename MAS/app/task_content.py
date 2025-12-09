"""
Task-Inhalte fuer die Studie zum internationalen Markteintritt
Dieses Modul enthaelt alle Aufgabenbeschreibungen, Materialien und Inhalte fuer das AMG-Experiment.
"""

STUDY_TITLE = "Internationaler Markteintritt eines deutschen Software-Start-ups"

STUDY_INTRODUCTION = """
Danke fuer deine Teilnahme! Du erstellst heute eine Concept Map – eine visuelle Darstellung von Konzepten und ihren Beziehungen. Stell dir eine Concept Map wie eine Landkarte vor: Staedte (= Konzepte) sind durch Strassen (= Beziehungen) verbunden.

**Eine Concept Map besteht aus:**
- **Beschrifteten Knoten:** Die Konzepte (Kreise)
- **Beschrifteten Kanten:** Pfeile, die Konzepte verbinden
- **Beziehungen:** Jeder Pfeil hat eine Beschriftung fuer die Art der Beziehung

**Beispiel:** [Marktanalyse] ---erlaubt---> [Identifikation von Zielmaerkten]
"""

TASK_DESCRIPTION = """
## Aufgabenbeschreibung

Diese Studie untersucht Herausforderungen, die ein Start-up beim internationalen Markteintritt bewaeltigen muss. Verschiedene Faktoren spielen zusammen und beeinflussen sich gegenseitig.

**Wichtig:** Der Markteintritt findet unter dem Standard Adaptive Market Gatekeeping (AMG) statt. Das zentrale Konzept, das du in deiner Analyse beruecksichtigen musst, ist **Adaptive Market Gatekeeping (AMG)** (entwickelt 2023 von einer OECD-Arbeitsgruppe).

### Was ist AMG?

Angenommen, du willst mit deinem Start-up in einen neuen Markt (z. B. China oder USA) eintreten. Etablierte Unternehmen wollen ihre Position schuetzen. AMG beschreibt, wie diese „Incumbents“ gemeinsam und in Echtzeit die Spielregeln aendern, um den Eintritt fuer Neueinsteiger zu erschweren. Dazu gehoeren:

- **Dynamische Anpassung:** Etablierte beobachten neue Start-ups und passen ihre Abwehr flexibel an
- **Regelaenderung:** Sie beeinflussen Standards, Zertifizierungen oder informelle Marktregeln zu ihren Gunsten
- **Netzwerkkontrolle:** Kontrolle ueber Schluessellieferanten, Vertriebskanaele oder Partnernetzwerke
- **Ressourcenblockade:** Sie binden knappe Ressourcen (z. B. Fachkraefte, Produktionskapazitaet)

### Beispiel:
Das deutsche Software-Start-up „Veyra“ will in den japanischen Markt. Durch AMG koennen lokale Wettbewerber:
- Neue technische Standards einfuehren, die nur ihre Produkte erfuellen
- Exklusive Vertraege mit wichtigen Distributoren sichern
- Preise temporaer senken, um den Eintritt unprofitabel zu machen

## Deine Aufgabe

Erstelle mit der bereitgestellten Oberflaeche eine Concept Map, die zeigt, wie folgende Konzepte beim internationalen Markteintritt des Start-ups zusammenhaengen. Hebe hervor, wie das Start-up AMG navigieren kann.

### Konzepte (eigene, konkrete Benennung erlaubt):

1. Marktanalyse (Untersuchung potenzieller Maerkte, Wettbewerbssituation im Zielmarkt)
2. Ressourcen (Kapital, Personal, Know-how)
3. Eintrittsstrategien (Wege in den Markt):
   - Export (Warenversand aus dem Heimatland)
   - Joint Venture (Partnerschaft mit lokalem Unternehmen)
   - Direktinvestition (eigene Tochtergesellschaft gruenden)
4. AMG (Adaptive Market Gatekeeping – siehe oben)

### Anforderungen

- Verwende konkrete, relevante Konzepte (z. B. „Kredit“ als Knoten bei „Finanzierung“)
- Verbinde Konzepte mit kurzen, beschrifteten Pfeilen (z. B. beeinflusst, ermoeglicht, verhindert, ist Voraussetzung fuer, verstaerkt, reduziert)
- Erstelle mindestens 6 Verbindungen; mehr, wenn sinnvoll
- Besonderer Fokus: Wie beeinflusst AMG die anderen Faktoren?

### Format

Du arbeitest in 5 Runden (je ca. 5–10 Minuten). In jeder Runde kannst du deine Map mit Hilfe der Chatbots erweitern/verbessern.

**Tipp:** Starte mit offensichtlichen Verbindungen und fuege dann komplexere Beziehungen hinzu. AMG ist ein Mechanismus etablierter Firmen – ueberlege, wie es die Aspekte des Markteintritts beeinflusst.
"""

EXTRA_MATERIALS = """
## Konzepte mit Beschreibungen

**1. Marktanalyse** – Systematische Sammlung und Bewertung von Informationen ueber potenzielle Maerkte. Umfasst typischerweise Marktgroesse, erwartetes Wachstum, Kundennachfrage, relevante Trends sowie Wettbewerb (Anzahl der Konkurrenten, Marktanteile, Strategien). Erfolgsfaktoren: Product-Market-Fit, Anpassung an lokale Beduerfnisse, verlaessliche Partner, wettbewerbsfaehige Preise, effiziente Lieferketten.

**2. Ressourcen** – Finanzielle, personelle und wissensbasierte Mittel eines Start-ups: Kapitalreserven, qualifizierte Mitarbeitende, Management-Expertise, technologisches Know-how, Netzwerke.

**3. Eintrittsstrategien** – Strategische Ansaetze, um in einen neuen Markt zu gehen; unterscheiden sich in Risiko, Kontrolle und Ressourceneinsatz.
   - **Export** – Waren direkt aus dem Heimatland liefern, minimale lokale Praesenz.
   - **Joint Venture** – Kooperation mit einem lokalen Unternehmen zum Teilen von Ressourcen, Risiken und Markt-Know-how.
   - **Direktinvestition** – Eigene Tochter oder Niederlassung gruenden: volle Kontrolle, aber hoher Aufwand; erfordert oft starke Marke, Umgang mit Regulierung, Aufbau von Kanaelen.

**4. AMG (Adaptive Market Gatekeeping)** – Mechanismus, der Markteintritt reguliert und bewertet. Agiert als dynamischer Filter, der sich an Kontextbedingungen anpasst und bestimmt, ob ein Unternehmen Zugang erhaelt oder fortschreiten kann.
"""

# Initial concept map for the AMG task
INITIAL_CONCEPT_MAP = {
    "elements": [
        {
            "data": {
                "id": "amg",
                "label": "Adaptive Market Gatekeeping (AMG)",
                "x": 400,
                "y": 300
            }
        }
    ]
}

# Expert concept map for AMG task (for comparison and assessment)
EXPERT_CONCEPT_MAP = {
    "nodes": [
        "AMG", "Market Analysis", "Target Markets", "Competitive Environment",
        "Entry Barriers", "Legal Framework", "Start-up Resources", 
        "Export Strategy", "Joint Venture", "Direct Investment",
        "Financing", "Marketing Strategy", "Success Factors",
        "Dynamic Adaptation", "Rule-changing", "Network Control", "Resource Blocking"
    ],
    "edges": [
        {"source": "Market Analysis", "target": "Target Markets", "relation": "enables"},
        {"source": "AMG", "target": "Entry Barriers", "relation": "increases"},
        {"source": "Competitive Environment", "target": "AMG", "relation": "activates"},
        {"source": "AMG", "target": "Legal Framework", "relation": "influences"},
        {"source": "Start-up Resources", "target": "Entry Strategies", "relation": "determines"},
        {"source": "AMG", "target": "Network Control", "relation": "implements"},
        {"source": "Network Control", "target": "Marketing Strategy", "relation": "restricts"},
        {"source": "AMG", "target": "Resource Blocking", "relation": "utilizes"},
        {"source": "Resource Blocking", "target": "Start-up Resources", "relation": "reduces"},
        {"source": "Financing", "target": "Direct Investment", "relation": "enables"},
        {"source": "Legal Framework", "target": "Joint Venture", "relation": "regulates"},
        {"source": "AMG", "target": "Success Factors", "relation": "challenges"},
        {"source": "Dynamic Adaptation", "target": "Entry Strategies", "relation": "counters"},
        {"source": "Rule-changing", "target": "Legal Framework", "relation": "modifies"},
        {"source": "Target Markets", "target": "Marketing Strategy", "relation": "shapes"}
    ]
}
