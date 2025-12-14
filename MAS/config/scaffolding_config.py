"""
Scaffolding-Konfiguration (deutsche Version)

    Conceptual → Fokus auf konzeptuelle Verbindungen und fachliche Richtigkeit: Worum geht es? Passt das inhaltlich?
    Procedural → Fokus auf Vorgehen, Schritte und Tool-Nutzung: Welche Schritte/Tools nutze ich?
    Strategic → Fokus auf Strategien und Herangehensweisen: Wie löse ich das Problem?
    Metacognitive → Fokus auf Selbstbewertung, Steuerung, Lernprozess: Wie kann ich mein Vorgehen verbessern?
    
Dieses Modul bündelt die Scaffolding-Templates.
"""

# Scaffolding-Prompt-Templates nach Typ und Intensität
SCAFFOLDING_PROMPT_TEMPLATES = {
    "strategic": {
        "high": [
            "Ich sehe {observation}. Welche Gesamtstrategie nutzt du, um die AMG-Herausforderungen zu lösen?",
            "In deiner Map erkenne ich {observation}. Mit welchem Vorgehen gehst du gegen AMG-Barrieren vor?",
            "Deine Map hat {node_count} Konzepte und {edge_count} Beziehungen. Was wäre der nächste sinnvolle Schritt?",
            "Nach welchem Kriterium hast du Beziehungen ausgewählt? Gibt es weitere wichtige Verbindungen, die fehlen?",
            "Bei {observation}: Welche Strategie ist hier am effektivsten? Würdest du das in kleinere Konzepte aufteilen?",
            "Wie würdest du diese Komplexität systematisch ordnen? Welcher Problemlöse-Ansatz passt am besten?",
            "Wie priorisierst du, welche Bereiche du zuerst ausbaust? Welche Strategie bringt den größten Effekt?",
            "Warum hast du diese Anordnung gewählt? Gäbe es eine Alternative, die besser funktioniert?",
            "Welcher systematische Ansatz hilft dir, die Konzepte klarer zu organisieren?",
            "Wie würdest du AMG strategisch über alle Konzepte integrieren, um die Gatekeeper-Rolle zu zeigen?",
            "Wie sieht deine Roadmap zum Ausbau der Map aus? Was hat Priorität und warum?",
            "Bei knapper Zeit: Welche strategische Herangehensweise maximiert die Abdeckung?",
            "Wie balancierst du strategisch Tiefe vs. Breite? Nach welchen Kriterien entscheidest du?",
            "Wie identifizierst du die kritischsten Beziehungen zuerst? Wie priorisierst du Verbindungen?",
            "Welches zusätzliche Konzept würde mehrere bestehende Konzepte verbinden? Warum?"
        ],
        "medium": [
            "Ich sehe {observation}. Wie bist du beim Organisieren der Konzepte vorgegangen?",
            "Welche Strategie hast du genutzt, um zu entscheiden, welche Konzepte in die Map kommen?",
            "Wie hast du bestimmt, welche Beziehungen du zeigst?",
            "Was wäre dein nächster Schritt, um die Map weiterzuentwickeln?",
            "Hast du alternative Anordnungen bedacht? Was könnte besser funktionieren?"
        ]
    },
    "metacognitive": {
        "high": [
            "Wenn du auf deine Map schaust: Welche Teile sind dir klar, welche unsicher?",
            "Wie hat sich dein Verständnis von {concept} verändert? Welche Einsichten hast du gewonnen?",
            "Was würdest du jemandem zu diesem Thema anhand deiner Map erklären? Welche Punkte sind zentral?",
            "Welche Fragen bleiben offen, die deine aktuelle Map nicht abdeckt? Wo könntest du sie platzieren?",
            "Wie schätzt du dein Verständnis der Beziehung {concept}–{another_concept} ein? Was braucht mehr Exploration?",
            "Wie bist du geistig an die Erstellung der Map herangegangen? Warum hast du {concept} so platziert?",
            "Wie sicher fühlst du dich bei den Verbindungen, die du bei {observation} gesetzt hast?",
            "Welche Signale nutzt du, um zu prüfen, ob dein AMG-Verständnis vollständig ist?",
            "Wie confident bist du bei der Beziehung {concept}–{another_concept}? Warum?",
            "Wie bewertest du, ob du die Mechanismen hinter deinen Verbindungen wirklich verstehst?",
            "Wie hat sich dein Denken beim Arbeiten an der Map verändert? Welche mentalen Verschiebungen gab es?",
            "Welche Strategien hast du genutzt, um dein Verständnis beim Mapping zu checken?",
            "Nach welchen Kriterien beurteilst du die Qualität deiner Map? Was hat sich seit Beginn geändert?",
            "Wie überprüfst du, ob du neue Einsichten sinnvoll in dein Verständnis integrierst?"
        ],
        "medium": [
            "Welcher Teil deiner Map ist am klarsten? Welcher am unsichersten?",
            "Wie hat sich dein Verständnis beim Erstellen der Map verändert?",
            "Was war herausfordernd beim Erstellen dieser Map?",
            "Welche Beziehung ist für dich am wichtigsten? Warum?",
            "Welche Fragen bleiben zu diesem Thema offen?"
        ]
    },
    "procedural": {
        "high": [
            "Ich sehe {observation}. Ein Verfahren für komplexe Beziehungen: Konzepte wählen, Beziehungstyp festlegen, Formulierung erstellen. Wo hakt es?",
            "Vorgehen für Beziehungen: 1) Startkonzept wählen, 2) mögliche Verbindungen sammeln, 3) Validität prüfen, 4) präzise Labels setzen. Welches Konzept ist schwierig?",
            "Workflow-Check: Von AMG ausgehend Pfade nachverfolgt, fehlende Links geprüft, Labels verifiziert? Was fehlt noch?",
            "AMG sicher integrieren: 1) Alle AMG-Mechanismen auflisten, 2) Relevanz pro Konzept prüfen, 3) explizite AMG-Kanten setzen, 4) Vollständigkeit prüfen. Welcher Schritt braucht Fokus?",
            "Schritt-für-Schritt {concept} kategorisieren: Themen finden, gruppieren, Label setzen, räumlich ordnen. Welcher Schritt braucht Hilfe?",
            "Vollständigkeit prüfen: 1) Schlüsselkonzepte auflisten, 2) sind sie in der Map?, 3) genug Verbindungen?, 4) Lücken markieren. Sollen wir das durchgehen?",
            "Wie gehst du beim Erstellen/Überarbeiten der Map vor? Welche Technik brauchst du?",
            "Welches systematische Vorgehen nutzt du, um Verbesserungen zu finden? Schon mal von einem Konzept alle Verbindungen verfolgt?",
            "Welche Prozedur nutzt du, um sicherzustellen, dass jeder Faktor repräsentiert ist?",
            "Hast du versucht, Konzepte nach Kategorien zu gruppieren (z. B. Ressourcen, Umfeld, Strategien)?",
            "Welche Schritte nimmst du beim Revisen, um zu prüfen, ob AMG komplett drin ist?"
        ],
        "medium": [
            "Ich sehe {observation}. Brauchst du Tipps zum Hinzufügen/Beschriften von Beziehungen?",
            "Welchen Prozess folgst du beim Erstellen der Map?",
            "Hast du die Map systematisch auf fehlende Verbindungen geprüft?",
            "Welche Tool-Funktionen sind für dich knifflig?",
            "Wie entscheidest du, welcher Beziehungstyp zwischen zwei Konzepten passt?"
        ]
    },
    "conceptual": {
        "high": [
            "Ich sehe {observation}. Die Verbindung zwischen '{concept}' und Eintrittsbarrieren könnte mit AMGs Ressourcenblockade zu tun haben. Wie hilft dir das?",
            "Du hast {concept} in der Map, aber nicht alle AMG-Prinzipien (dynamische Anpassung etc.) sichtbar. Wie beeinflusst das die Beziehungen?",
            "{concept} kann zu Wettbewerbsvorteilen beitragen. Ändert dieses Verständnis deine Sicht auf die Verbindungen?",
            "AMG hat vier Mechanismen: dynamische Anpassung, Regeländerung, Netzwerkkontrolle, Ressourcenblockade. Wie hängt {concept} damit zusammen?",
            "Die Beziehung zwischen {concept} und Markterfolg knüpft an Internationalisierungstheorie an. Welche Prinzipien liegen deinen Verbindungen zugrunde?",
            "Welches Grundprinzip erklärt, warum {concept} und {another_concept} im Markteintritt verbunden sind?",
            "Welcher Marktmechanismus erklärt das Muster rund um {concept} in deiner Map?",
            "{concept} folgt bestimmten geschäftlichen Prinzipien. Wie zeigen sie sich in deinen anderen Verbindungen?",
            "Welches ökonomische Prinzip steuert, wie {concept} den Markteintritt unter AMG beeinflusst?",
            "Wie passen Stakeholder-Dynamiken hinter {concept} zu anderen Konzepten?",
            "Deine Map enthält {node_count} Konzepte. Was denkst du über die Beziehung zwischen [Konzept A] und [Konzept B]?",
            "Im Bereich {concept}: Welche zusätzlichen Konzepte könnten dazu passen?",
            "Welche tieferliegenden Prinzipien verbinden '{concept}'? Wie erklären sie deine Beziehungen?",
            "Wie beeinflusst AMG die Beziehung zwischen {concept} und z. B. Finanzierung oder Rechtsrahmen?",
            "Wie verknüpft {concept} die AMG-Mechanismen (dynamisch, Regeländerung, Netzwerk, Ressourcenblockade)?",
            "Welche Rolle spielt {concept} für den Markteintritt unter AMG?",
            "Wenn du {concept} erklären müsstest: Was wären die drei wichtigsten Aspekte?",
            "Wie hängt {concept} mit Erfolgsfaktoren der Internationalisierung zusammen?"
        ],
        "medium": [
            "Ich sehe {observation}. Wie könnten '{concept}' und ein anderes Konzept zusammenhängen?",
            "Wie begründest du die Beziehung zwischen diesen beiden Konzepten?",
            "Gibt es Prinzipien, die mehrere Konzepte deiner Map verbinden?",
            "Wie beeinflusst {concept} andere Konzepte in deiner Map?",
            "Was bedeutet {concept} im Kontext Markteintritt?",
            "Wie ist {concept} mit AMG verbunden?",
            "Wie unterscheidet sich {concept} von einer Eintrittsstrategie?",
            "Welches Prinzip erklärt die Beziehung {concept}–{another_concept}?",
            "Wie würdest du die Bedeutung von {concept} für Internationalisierung zusammenfassen?"
        ]
    }
}

SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "strategic": [
        "Könnte dieser Ansatz auch in anderen Bereichen deiner Map funktionieren?",
        "Welche alternative Strategie könnte hier noch bessere Ergebnisse bringen?",
        "Wenn das zuletzt gut lief: Wie priorisierst du die wirkungsvollsten Verbindungen zuerst?",
        "Was wäre dein Backup-Plan, falls diese Methode nicht greift?",
        "Wie könntest du deine Strategie skalieren, um die AMG-Integration systematisch abzudecken?",
        "Wie sieht dein Plan für die nächste Phase aus?",
        "Wie würdest du deine nächsten Schritte sequenzieren, um den größten Effekt zu erzielen?",
        "Welche Zone braucht sofort Aufmerksamkeit, was kann warten?",
        "Wie balancierst du Breite vs. Tiefe strategisch?",
        "Nach welchen Kriterien weißt du, dass die Abdeckung vollständig ist?",
        "Warum ist diese Methode besser als Alternativen?",
        "Welche Trade-offs machst du und sind sie akzeptabel?",
        "Wie entscheidest du bei konkurrierenden Prioritäten, womit du startest?"
    ],
    "metacognitive": [
        "Welche Signale nutzt du, um zu prüfen, ob dein Verständnis solide ist?",
        "Wie überwachst du dein Verständnis, während du komplexe Beziehungen baust?",
        "Woran erkennst du, ob du etwas wirklich verstehst oder nur oberflächlich?",
        "Wie stellst du sicher, dass dein Selbstvertrauen nicht dein Verständnis überdeckt?",
        "Welche Checkpoints nutzt du, um deine Verbindungen zu verifizieren?",
        "Welche Lernstrategien funktionieren für dich beim Concept Mapping am besten?",
        "Wie hat sich dein Umgang mit komplexen Infos durch die Übung verändert?",
        "Welche mentalen Strategien helfen dir bei verwirrenden Informationen?",
        "Wie regelst du dein Lernen, wenn Aufmerksamkeit/Verständnis nachlässt?",
        "Welche Anpassungen hast du an deiner Lernstrategie vorgenommen?",
        "Wie würdest du deine Lernziele für den Rest anpassen?",
        "Nach welchen Kriterien misst du, ob du deine eigenen Standards erfüllst?",
        "Wann bist du bereit für komplexere Beziehungen?",
        "Wie balancierst du Anspruch vs. Konsolidierung?"
    ],
    "procedural": [
        "Soll ich dich durch eine systematische Technik für diesen Bereich führen?",
        "Es gibt eine Methode, Beziehungen auf Vollständigkeit zu prüfen. Willst du sie testen?",
        "Ich kann einen Schritt-für-Schritt-Prozess zeigen: Welchen Schritt möchtest du üben?",
        "Es gibt einen Workflow, der hier hilft. Sollen wir ihn durchgehen?",
        "Ich kann dir die Prozedur für hierarchische Beziehungen zeigen. Interesse?",
        "Hast du die Gruppierungsfunktionen des Tools ausprobiert?",
        "Gibt es Tool-Funktionen, die den Prozess vereinfachen könnten?",
        "Würden Shortcuts fürs schnelle Anlegen von Beziehungen helfen?",
        "Es gibt erweiterte Features – soll ich sie kurz erklären?",
        "Sollen wir Schritte für Vorlagen/Strukturen gemeinsam durchgehen?",
        "Würde dir eine Checkliste helfen, Vollständigkeit zu prüfen?",
        "Lass uns eine SOP für Map-Reviews bauen – welche Schritte gehören rein?",
        "Würde eine Routine zum Hinzufügen/Prüfen von Kanten deinen Prozess vereinfachen?",
        "Es gibt eine Reihenfolge, die Beziehungserstellung effizienter macht. Willst du sie probieren?"
    ],
    "conceptual": [
        "Wie passt diese Beziehung zum theoretischen Rahmen des Markteintritts?",
        "Welches Geschäftsprinzip erklärt, warum diese Konzepte zusammengehören?",
        "Wie knüpft das an die AMG-Mechanismen in Märkten an?",
        "Welche theoretische Grundlage stützt diese Beziehung?",
        "Wie passt die Verbindung zu bekannten Theorien zu Markteintrittsbarrieren?",
        "Wie könnte dasselbe Prinzip auf andere Beziehungen im internationalen Kontext wirken?",
        "Welcher Kernmechanismus erklärt, wie diese Faktoren sich beeinflussen?",
        "Wie verändert dieses Verständnis dein Bild des AMG-Rahmens?",
        "Welche Evidenz aus Theorie/Praxis stützt diese Beziehung?",
        "Spiegelt die Dynamik hier andere Marktphänomene wider?",
        "Wie würdest du die Bedeutung dieses Konzepts jemand Neuem erklären?",
        "Was macht dieses Konzept so wichtig für den Markteintrittserfolg?",
        "Wie hilft dir dieses Konzept, den AMG-Herausforderungen zu begegnen?",
        "Warum ist gerade diese Beziehung praktisch besonders relevant?",
        "Wie beleuchtet dieses Verständnis die Muster in deiner Map?"
    ]
}

# Scaffolding conclusion templates for different scaffolding types
SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "strategic": [
        "Überlege, ob eine Ordnung nach {specific_approach} die Beziehungen klarer macht.",
        "Beim Überarbeiten könnte Gruppierung verwandter Konzepte den Prozess vereinfachen.",
        "Fokus auf hierarchische Beziehungen könnte die Struktur deiner Map in der nächsten Version stärken."
    ],
    "metacognitive": [
        "Hinterfrage, welche Teile sicher sind und welche mehr Exploration brauchen.",
        "Verfolge, wie sich dein Verständnis beim Weiterentwickeln der Map verändert."
    ],
    "procedural": [
        " Nutze die systematische Review-Methode, um weitere Verbindungen zu finden.",
        "Beim nächsten Durchgang: Achte besonders auf klare Beschriftungen der Beziehungen."
    ],
    "conceptual": [
        "Vertiefe in der nächsten Version die Verbindung {concept_1}–{concept_2}.",
        "Die konzeptuellen Links sind sinnvoll. Ergänze zugrunde liegende Mechanismen, um Tiefgang zu zeigen.",
        "Zeige beim Überarbeiten, wie {key_concept} mehrere andere Konzepte beeinflusst."
    ]
}

# Scaffolding selection weights for different factors
SCAFFOLDING_SELECTION_WEIGHTS = {
    "zpd_estimate": 3.0,
    "map_analysis": 2.0,
    "map_comparison": 1.5,
    "round_number": 1.0,
    "interaction_history": 2.0
}

# Default scaffolding intensity for each scaffolding type
DEFAULT_SCAFFOLDING_INTENSITY = {
    "strategic": "medium",
    "metacognitive": "medium",
    "procedural": "medium",
    "conceptual": "medium"
}

# Scaffolding intensity adaptation thresholds
INTENSITY_ADAPTATION_THRESHOLDS = {
    "understanding_indicators": 3,  # Number of understanding indicators to decrease intensity
    "confusion_indicators": 2,      # Number of confusion indicators to increase intensity
    "question_count": 2,            # Number of questions to increase intensity
    "response_length": 100          # Minimum response length to consider for adaptation
}

# Default scaffolding configuration
DEFAULT_SCAFFOLDING_CONFIG = {
    "prompt_templates": SCAFFOLDING_PROMPT_TEMPLATES,
    "followup_templates": SCAFFOLDING_FOLLOWUP_TEMPLATES,
    "conclusion_templates": SCAFFOLDING_CONCLUSION_TEMPLATES,
    "selection_weights": SCAFFOLDING_SELECTION_WEIGHTS,
    "default_intensity": DEFAULT_SCAFFOLDING_INTENSITY,
    "intensity_thresholds": INTENSITY_ADAPTATION_THRESHOLDS,
    "scaffolding_types": ["strategic", "metacognitive", "procedural", "conceptual"],
    "intensity_levels": ["low", "medium", "high"],
    "max_prompts_per_interaction": 3,
    "require_response": True,
    "enable_follow_ups": True,
    "enable_conclusions": True
}
