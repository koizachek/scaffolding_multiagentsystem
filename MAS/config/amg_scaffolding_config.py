"""
AMG-spezifische Scaffolding-Konfiguration (deutsche Version)

Dieses Modul enthaelt Scaffolding-Vorlagen fuer die AMG-Markteintrittsaufgabe.
"""

# AMG-specific scaffolding prompt templates
AMG_SCAFFOLDING_PROMPT_TEMPLATES = {
    "conceptual": {
        "high": [
            "Ich sehe, du hast {observation} ergaenzt. Wie koennte das AMG-Eintrittsbarrieren beeinflussen?",
            "Deine Concept Map hat {node_count} Konzepte. Welche Prinzipien verbinden die Markteintrittsstrategien?",
            "In deiner Map ist {concept}. Wie koennte AMGs Ressourcenblockade die Ressourcen eines Start-ups konzeptionell betreffen?",
            "Du hast Marktanalyse und Zielmaerkte. Wie verknuepfen sie sich mit AMGs Netzwerkkontrolle?",
            "Spannende Platzierung von {concept}. Wie koennte der Rechtsrahmen durch AMGs Regelanderung beeinflusst werden?",
            "Wie wirken AMGs Mechanismen auf deine Finanzierungskonzepte? Welche Prinzipien steuern das?"
        ],
        "medium": [
            "Wie haengt AMG mit den Eintrittsbarrieren deiner Map zusammen?",
            "Welche Verbindung besteht zwischen AMG und deinen Eintrittsstrategien?",
            "Wie koennten AMGs Mechanismen die Ressourcen des Start-ups beeinflussen?",
            "Welche Beziehung siehst du zwischen Marktanalyse und AMG?",
            "Wie interagiert der Rechtsrahmen mit AMG in deiner Map?"
        ],
        "low": [
            "Welche Konzepte sind am staerksten von AMG betroffen?",
            "Wie ist AMG mit anderen Konzepten verbunden?",
            "Welcher AMG-Mechanismus ist am wichtigsten?",
            "Was ist die Hauptbeziehung zwischen AMG und Markteintritt?"
        ]
    },
    "procedural": {
        "high": [
            "Ich sehe {observation}. Hast du fuer jeden AMG-Mechanismus (dynamisch, Regelanderung, Netzwerk, Ressourcenblockade) die Effekte auf den Markteintritt nachverfolgt?",
            "Wie entscheidest du, welche Eintrittsstrategien du mit AMG verknuepfst? Hast du das Beispiel als Vorlage genutzt?",
            "Welche Beschriftung nutzt du fuer AMG-Beziehungen? Aktionsverben wie „blockiert“, „beeinflusst“, „kontert“ helfen.",
            "Hast du Konzepte in Ebenen geordnet (AMG-Mechanismen, Strategien, Ressourcen), um den Einflussfluss zu zeigen?",
            "Wie identifizierst du Gegenstrategien, damit das Start-up AMG navigieren kann? Von Erfolgsfaktoren rueckwaerts denken hilft.",
            "Pruefst du systematisch, ob jeder AMG-Mechanismus mindestens eine Verbindung hat? So deckst du AMGs Wirkung ab."
        ],
        "medium": [
            "Hast du von jedem AMG-Mechanismus aus die Effekte nachgezeichnet?",
            "Welchen Prozess nutzt du, um AMG mit Eintrittsstrategien zu verbinden?",
            "Wie waehlst du Labels fuer AMG-Beziehungen?",
            "Hast du ueberlegt, Konzepte nach Rolle in Ebenen zu ordnen?",
            "Welche Vorgehensweise hilft dir, AMG-Navigation zu zeigen?"
        ],
        "low": [
            "Wie entscheidest du, welche Konzepte du mit AMG verknuepfst?",
            "Was hilft dir bei der Beschriftung von AMG-Beziehungen?",
            "Welche Anordnung von AMG in der Map hast du ausprobiert?",
            "Welcher Prozess hilft dir, AMGs Einfluss zu zeigen?"
        ]
    },
    "strategic": {
        "high": [
            "Ich sehe {observation}. Wie zeigst du strategisch die Reaktion des Start-ups auf AMG? Wie stellst du Herausforderungen und Loesungen dar?",
            "Deine Map hat {node_count} Konzepte. Warum positionierst du AMG so? Sollte AMG zentral stehen, um die Gatekeeper-Rolle zu zeigen?",
            "Welche Strategie nutzt du, um darzustellen, dass AMG mehrere Aspekte gleichzeitig beeinflusst? Unterschiedliche Beziehungstypen koennten direkt/indirekt zeigen.",
            "Struktur mit {concept}: Wie trennst du strategisch AMGs blockierende vs. adaptive Effekte? Diese Unterscheidung staerkt die Map.",
            "Wie zeigst du den Zeitverlauf – wie AMG sich an neue Strategien anpasst? Diese Dynamik ist zentral.",
            "Nach welchen Kriterien waehlst du die kritischsten Verbindungen, um erfolgreiche AMG-Navigation zu zeigen?"
        ],
        "medium": [
            "Wie zeigst du AMGs Herausforderungen und moegliche Loesungen?",
            "Wie hast du entschieden, wo AMG steht?",
            "Welche Vorgehensweise hilft dir, AMGs vielfaeltige Wirkungen zu zeigen?",
            "Wie machst du Blockieren vs. Anpassen sichtbar?",
            "Wie zeigst du die wichtigsten AMG-Beziehungen?"
        ],
        "low": [
            "Was ist deine Gesamtstrategie, um AMG anzuordnen?",
            "Wie hast du entschieden, welche AMG-Effekte zuerst kommen?",
            "Welche Vorgehensweise hilft dir, AMGs Beziehungen zu strukturieren?",
            "Welche AMG-Verbindungen sind strategisch am wichtigsten?"
        ]
    },
    "metacognitive": {
        "high": [
            "Welche AMG-Aspekte sind dir klar, welche unklar? Warum sind die unklaren schwierig?",
            "Wie hat sich dein Verstaendnis von AMGs Rolle im Markteintritt veraendert? Welche Einsichten hast du gewonnen?",
            "Im Vergleich zum Beispiel: Wie gut erfasst deine Map aehnliche Dynamiken? Was koennte bei AMG-Effekten fehlen?",
            "Wenn du AMG erklaeren muesstest: Welche Schluesselbeziehungen wuerdest du betonen? Was fehlt noch?",
            "Wie sicher bist du, dass deine Map zeigt, wie ein Start-up AMG navigiert? Welche Bereiche brauchen mehr Gedanken?",
            "Welche Annahmen triffst du ueber AMG? Wie wuerde die Map sich aendern, wenn du sie hinterfragst?"
        ],
        "medium": [
            "Welche Teile von AMG verstehst du am besten, welche sind unklar?",
            "Wie hat sich dein AMG-Verstaendnis beim Erstellen der Map veraendert?",
            "Wie gut erklaert deine Map das Veyra-Beispiel?",
            "Welche AMG-Beziehungen wuerdest du hervorheben, um sie anderen zu erklaeren?",
            "Wie sicher bist du bei Wegen, AMG zu navigieren?"
        ],
        "low": [
            "Was verstehst du an AMG am besten?",
            "Was ist an AMGs Rolle noch verwirrend?",
            "Wie hat sich dein Denken ueber AMG veraendert?",
            "Was moechtest du an AMG besser verstehen?"
        ]
    }
}

# AMG-specific follow-up templates
AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "conceptual": [
        "Wie koennten andere AMG-Mechanismen (z. B. Netzwerkkontrolle oder Regelanderung) aehnliche Beziehungen erzeugen?",
        "Welche weiteren Konzepte koennte AMG nach demselben Prinzip beeinflussen?",
        "Wie wirkt sich diese AMG-Beziehung auf strategische Optionen aus? Welche Implikationen folgen?",
        "Wie hilft dieses Verstaendnis, Gegen- oder Anpassungswege an AMG zu finden?"
    ],
    "procedural": [
        "Hast du denselben Prozess systematisch fuer alle vier AMG-Mechanismen genutzt?",
        "Wuerde eine Checkliste der AMG-Effekte helfen, alle Bereiche abzudecken?",
        "Wie kannst du Gegenstrategien je Mechanismus systematisch identifizieren?",
        "Wie kannst du damit die zeitliche Abfolge von AMGs Anpassungen zeigen?"
    ],
    "strategic": [
        "Wie wuerde eine Reorganisation, die AMGs Gatekeeper-Rolle betont, die Aussage deiner Map aendern?",
        "Wie zeigst du am effektivsten Wege durch AMG-Barrieren?",
        "Koennte eine Gruppierung nach ‚von AMG betroffen‘ vs. ‚kontert AMG‘ Klarheit bringen?",
        "Wie kannst du die dynamisch-adaptive Natur von AMG im Zeitverlauf staerker betonen?"
    ],
    "metacognitive": [
        "Welcher AMG-Aspekt profitiert am meisten von weiterer Vertiefung?",
        "Wie beeinflusst dieses Verstaendnis deine Herangehensweise an aehnliche Geschaeftskonzepte?",
        "Welche Fragen zum Markteintritt kannst du nun beantworten?",
        "Wie hat das AMG-Verstaendnis deine Sicht auf Gruende fuer Scheitern bei Internationalisierung veraendert?"
    ]
}

# AMG-specific conclusion templates
AMG_SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "conceptual": [
        "Dein Verstaendnis ist fundiert. Pruefe, wie der Mechanismus {specific_mechanism} Kaskadeneffekte ueber mehrere Konzepte erzeugt.",
        "Die konzeptuellen Links entwickeln sich gut. Zeige als Naechstes, wie Rueckkopplungsschleifen entstehen.",
        "Du hast wichtige AMG-Beziehungen identifiziert. Fuege Konzepte hinzu, die zeigen, wie Start-ups Ressourcen einsetzen, um Mechanismen zu kontern."
    ],
    "procedural": [
        "Der systematische Ansatz hilft. Starte mit den vier Mechanismen und verfolge ihre Wirkungen methodisch.",
        "Achte darauf, dass jeder AMG-Mechanismus mit relevanten Strategien und Ressourcen verknuepft ist.",
        "Die prozeduralen Techniken greifen. Nutze konsistente Labels, die AMGs aktive Rolle markieren."
    ],
    "strategic": [
        "Erwaege eine Struktur, die Wege durch AMG-Barrieren staerker hervorhebt.",
        "Hebe als Naechstes die kritischsten Beziehungen fuer den Markteintritt hervor.",
        "Zeige deutlicher die zeitliche Dynamik von AMGs Anpassungsreaktionen."
    ],
    "metacognitive": [
        "Nutze die Einsichten, um festzulegen, welche AMG-Mechanismen du weiter vertiefen willst.",
        "Hinterfrage weiter deine Annahmen zum Funktionieren von AMG, waehrend du die Map ausbaust.",
        "Verfolge, wie sich deine Sicht auf Markteintritts-Herausforderungen mit tieferer Analyse aendert."
    ]
}

# Configuration for AMG task
AMG_SCAFFOLDING_CONFIG = {
    "prompt_templates": AMG_SCAFFOLDING_PROMPT_TEMPLATES,
    "followup_templates": AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES,
    "conclusion_templates": AMG_SCAFFOLDING_CONCLUSION_TEMPLATES,
    "task_context": {
        "main_concept": "Adaptive Market Gatekeeping (AMG)",
        "key_mechanisms": ["dynamische Anpassung", "Regelaenderung", "Netzwerkkontrolle", "Ressourcenblockade"],
        "example_company": "Veyra",
        "example_market": "japanischer Markt",
        "core_challenge": "AMG-Barrieren fuer erfolgreichen Markteintritt navigieren"
    },
    "concept_priorities": {
        "essential": ["AMG", "Eintrittsstrategien", "Eintrittsbarrieren", "Start-up-Ressourcen"],
        "important": ["Marktanalyse", "Zielmaerkte", "Wettbewerbsumfeld", "Rechtsrahmen"],
        "supporting": ["Finanzierung", "Marketingstrategie", "Erfolgsfaktoren"]
    },
    "relationship_suggestions": {
        "AMG_impacts": ["blockiert", "schraenkt ein", "beeinflusst", "erschwert", "verhindert", "erhoeht"],
        "counter_strategies": ["ueberwindet", "umgeht", "passt sich an", "mildert", "nutzt"],
        "enabling": ["ermoeglicht", "erleichtert", "unterstuetzt", "staerkt"],
        "causal": ["verursacht", "fuehrt zu", "resultiert in", "loest aus"]
    }
}
