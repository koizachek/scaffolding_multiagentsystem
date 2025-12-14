"""
AICCTP-spezifische Scaffolding-Konfiguration (deutsche Version)

Dieses Modul enthaelt Scaffolding-Vorlagen fuer die Aufgabe zum AI Carbon Credit Transfer Protocol (AICCTP).
"""

# AICCTP-specific scaffolding prompt templates
AMG_SCAFFOLDING_PROMPT_TEMPLATES = {
    "conceptual": {
        "high": [
            "Ich sehe, du hast {observation} ergaenzt. Wie koennte das AICCTP die Handelsbarrieren und Verifizierungen beeinflussen?",
            "Deine Concept Map hat {node_count} Konzepte. Welche Prinzipien verbinden die Teilnahmestrategien (Direkthandel, Makler, Konsortium)?",
            "In deiner Map ist {concept}. Wie koennte AICCTPs Verifizierungskomplexitaet die Faehigkeiten eines KMU belasten?",
            "Du hast Marktbedingungen und Regulatorische Standards. Wie verknuepfen sie sich mit AICCTPs Zugangssteuerung?",
            "Spannende Platzierung von {concept}. Wie koennte AICCTPs Preissignalisierung die Handelsbarrieren beeinflussen?",
            "Wie wirken AICCTP-Mechanismen auf deine Finanzierungs- und Kompetenz-Konzepte? Welche Prinzipien steuern das?"
        ],
        "medium": [
            "Wie haengt AICCTP mit den Handelsbarrieren deiner Map zusammen?",
            "Welche Verbindung besteht zwischen AICCTP und deinen Teilnahmestrategien?",
            "Wie koennten AICCTP-Mechanismen die KMU-Faehigkeiten beeinflussen?",
            "Welche Beziehung siehst du zwischen Marktbedingungen und AICCTP?",
            "Wie interagieren Regulatorische Standards mit AICCTP in deiner Map?"
        ],
        "low": [
            "Welche Konzepte sind am staerksten von AICCTP betroffen?",
            "Wie ist AICCTP mit anderen Konzepten verbunden?",
            "Welcher AICCTP-Mechanismus ist am wichtigsten?",
            "Was ist die Hauptbeziehung zwischen AICCTP und Marktteilnahme?"
        ]
    },
    "procedural": {
        "high": [
            "Ich sehe {observation}. Hast du fuer jeden AICCTP-Mechanismus (Verifizierungskomplexitaet, Transferverzoegerung, Preissignalisierung, Zugangssteuerung) die Effekte nachverfolgt?",
            "Wie entscheidest du, welche Teilnahmestrategien du mit AICCTP verknuepfst? Nutzt du das Beispiel als Vorlage?",
            "Welche Beschriftung nutzt du fuer AICCTP-Beziehungen? Aktionsverben wie „verzoegert“, „beguenstigt“, „erschwert“ helfen.",
            "Hast du Konzepte in Ebenen geordnet (Mechanismen, Strategien, Ressourcen/Kompetenzen), um den Einflussfluss zu zeigen?",
            "Wie identifizierst du Gegenstrategien, damit das KMU AICCTP navigieren kann? Von Erfolgsfaktoren rueckwaerts denken hilft.",
            "Pruefst du systematisch, ob jeder AICCTP-Mechanismus mindestens eine Verbindung hat? So deckst du AICCTPs Wirkung ab."
        ],
        "medium": [
            "Hast du von jedem AICCTP-Mechanismus aus die Effekte nachgezeichnet?",
            "Welchen Prozess nutzt du, um AICCTP mit Teilnahmestrategien zu verbinden?",
            "Wie waehlst du Labels fuer AICCTP-Beziehungen?",
            "Hast du ueberlegt, Konzepte nach Rolle in Ebenen zu ordnen?",
            "Welche Vorgehensweise hilft dir, die Navigation durch AICCTP zu zeigen?"
        ],
        "low": [
            "Wie entscheidest du, welche Konzepte du mit AICCTP verknuepfst?",
            "Was hilft dir bei der Beschriftung von AICCTP-Beziehungen?",
            "Welche Anordnung von AICCTP in der Map hast du ausprobiert?",
            "Welcher Prozess hilft dir, AICCTPs Einfluss zu zeigen?"
        ]
    },
    "strategic": {
        "high": [
            "Ich sehe {observation}. Wie zeigst du strategisch die Reaktion des KMU auf AICCTP? Wie stellst du Herausforderungen und Loesungen dar?",
            "Deine Map hat {node_count} Konzepte. Warum positionierst du AICCTP so? Sollte es zentral stehen, um die Gatekeeper-Rolle zu zeigen?",
            "Welche Strategie nutzt du, um darzustellen, dass AICCTP mehrere Aspekte gleichzeitig beeinflusst? Unterschiedliche Beziehungstypen koennten direkt/indirekt zeigen.",
            "Struktur mit {concept}: Wie trennst du strategisch AICCTPs blockierende vs. adaptive Effekte? Diese Unterscheidung staerkt die Map.",
            "Wie zeigst du den Zeitverlauf – wie AICCTP sich an Strategien kleinerer Akteure anpasst? Diese Dynamik ist zentral.",
            "Nach welchen Kriterien waehlst du die kritischsten Verbindungen, um erfolgreiche AICCTP-Navigation zu zeigen?"
        ],
        "medium": [
            "Wie zeigst du AICCTPs Herausforderungen und moegliche Loesungen?",
            "Wie hast du entschieden, wo AICCTP steht?",
            "Welche Vorgehensweise hilft dir, AICCTPs vielfaeltige Wirkungen zu zeigen?",
            "Wie machst du Verzoegerungen vs. Beguenstigungen sichtbar?",
            "Wie zeigst du die wichtigsten AICCTP-Beziehungen?"
        ],
        "low": [
            "Was ist deine Gesamtstrategie, um AICCTP anzuordnen?",
            "Wie hast du entschieden, welche AICCTP-Effekte zuerst kommen?",
            "Welche Vorgehensweise hilft dir, AICCTP-Beziehungen zu strukturieren?",
            "Welche AICCTP-Verbindungen sind strategisch am wichtigsten?"
        ]
    },
    "metacognitive": {
        "high": [
            "Welche AICCTP-Aspekte sind dir klar, welche unklar? Warum sind die unklaren schwierig?",
            "Wie hat sich dein Verstaendnis von AICCTPs Rolle im CO2-Handel veraendert? Welche Einsichten hast du gewonnen?",
            "Im Vergleich zum Beispiel: Wie gut erfasst deine Map aehnliche Dynamiken? Was koennte bei AICCTP-Effekten fehlen?",
            "Wenn du AICCTP erklaeren muesstest: Welche Schluesselbeziehungen wuerdest du betonen? Was fehlt noch?",
            "Wie sicher bist du, dass deine Map zeigt, wie ein KMU AICCTP navigiert? Welche Bereiche brauchen mehr Gedanken?",
            "Welche Annahmen triffst du ueber AICCTP? Wie wuerde die Map sich aendern, wenn du sie hinterfragst?"
        ],
        "medium": [
            "Welche Teile von AICCTP verstehst du am besten, welche sind unklar?",
            "Wie hat sich dein AICCTP-Verstaendnis beim Erstellen der Map veraendert?",
            "Wie gut erklaert deine Map das TechKlima-Beispiel?",
            "Welche AICCTP-Beziehungen wuerdest du hervorheben, um sie anderen zu erklaeren?",
            "Wie sicher bist du bei Wegen, AICCTP zu navigieren?"
        ],
        "low": [
            "Was verstehst du an AICCTP am besten?",
            "Was ist an AICCTPs Rolle noch verwirrend?",
            "Wie hat sich dein Denken ueber AICCTP veraendert?",
            "Was moechtest du an AICCTP besser verstehen?"
        ]
    }
}

# AICCTP-specific follow-up templates
AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "conceptual": [
        "Wie koennten andere AICCTP-Mechanismen (z. B. Preissignalisierung oder Zugangssteuerung) aehnliche Beziehungen erzeugen?",
        "Welche weiteren Konzepte koennte AICCTP nach demselben Prinzip beeinflussen?",
        "Wie wirkt sich diese AICCTP-Beziehung auf strategische Optionen aus? Welche Implikationen folgen?",
        "Wie hilft dieses Verstaendnis, Gegen- oder Anpassungswege an AICCTP zu finden?"
    ],
    "procedural": [
        "Hast du denselben Prozess systematisch fuer alle vier AICCTP-Mechanismen genutzt?",
        "Wuerde eine Checkliste der AICCTP-Effekte helfen, alle Bereiche abzudecken?",
        "Wie kannst du Gegenstrategien je Mechanismus systematisch identifizieren?",
        "Wie kannst du damit die zeitliche Abfolge von AICCTPs Anpassungen zeigen?"
    ],
    "strategic": [
        "Wie wuerde eine Reorganisation, die AICCTPs Gatekeeper-Rolle betont, die Aussage deiner Map aendern?",
        "Wie zeigst du am effektivsten Wege durch AICCTP-Barrieren?",
        "Koennte eine Gruppierung nach ‚von AICCTP betroffen‘ vs. ‚kontert AICCTP‘ Klarheit bringen?",
        "Wie kannst du die dynamisch-adaptive Natur von AICCTP im Zeitverlauf staerker betonen?"
    ],
    "metacognitive": [
        "Welcher AICCTP-Aspekt profitiert am meisten von weiterer Vertiefung?",
        "Wie beeinflusst dieses Verstaendnis deine Herangehensweise an aehnliche Marktteilnahme-Konzepte?",
        "Welche Fragen zum CO2-Handel kannst du nun beantworten?",
        "Wie hat das AICCTP-Verstaendnis deine Sicht auf Gruende fuer Scheitern bei Marktteilnahme veraendert?"
    ]
}

# AICCTP-specific conclusion templates
AMG_SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "conceptual": [
        "Dein Verstaendnis ist fundiert. Pruefe, wie der Mechanismus {specific_mechanism} Kaskadeneffekte ueber mehrere Konzepte erzeugt.",
        "Die konzeptuellen Links entwickeln sich gut. Zeige als Naechstes, wie Rueckkopplungsschleifen entstehen.",
        "Du hast wichtige AICCTP-Beziehungen identifiziert. Fuege Konzepte hinzu, die zeigen, wie KMU Ressourcen einsetzen, um Mechanismen zu kontern."
    ],
    "procedural": [
        "Der systematische Ansatz hilft. Starte mit den vier AICCTP-Mechanismen und verfolge ihre Wirkungen methodisch.",
        "Achte darauf, dass jeder AICCTP-Mechanismus mit relevanten Strategien und Ressourcen verknuepft ist.",
        "Die prozeduralen Techniken greifen. Nutze konsistente Labels, die AICCTPs aktive Rolle markieren."
    ],
    "strategic": [
        "Erwaege eine Struktur, die Wege durch AICCTP-Barrieren staerker hervorhebt.",
        "Hebe als Naechstes die kritischsten Beziehungen fuer die Marktteilnahme hervor.",
        "Zeige deutlicher die zeitliche Dynamik von AICCTPs Anpassungsreaktionen."
    ],
    "metacognitive": [
        "Nutze die Einsichten, um festzulegen, welche AICCTP-Mechanismen du weiter vertiefen willst.",
        "Hinterfrage weiter deine Annahmen zum Funktionieren von AICCTP, waehrend du die Map ausbaust.",
        "Verfolge, wie sich deine Sicht auf Marktteilnahme-Herausforderungen mit tieferer Analyse aendert."
    ]
}

# Configuration for AICCTP task
AMG_SCAFFOLDING_CONFIG = {
    "prompt_templates": AMG_SCAFFOLDING_PROMPT_TEMPLATES,
    "followup_templates": AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES,
    "conclusion_templates": AMG_SCAFFOLDING_CONCLUSION_TEMPLATES,
    "task_context": {
        "main_concept": "AI Carbon Credit Transfer Protocol (AICCTP)",
        "key_mechanisms": ["Verifizierungskomplexitaet", "Transferverzoegerungen", "Preissignalisierung", "Zugangssteuerung"],
        "example_company": "TechKlima",
        "example_market": "regionaler AI-CO2-Markt (z. B. EU)",
        "core_challenge": "AICCTP-Barrieren fuer erfolgreiche KMU-Teilnahme navigieren"
    },
    "concept_priorities": {
        "essential": ["AICCTP", "Teilnahmestrategien", "Handelsbarrieren", "Verifizierungsprozess", "KMU-Faehigkeiten"],
        "important": ["CO2-Fussabdruck-Bewertung", "Marktbedingungen", "Regulatorische Standards", "Preis-Signalisierung"],
        "supporting": ["Transferverzoegerungen", "Verifizierungskomplexitaet", "Zugangssteuerung"]
    },
    "relationship_suggestions": {
        "AICCTP_impacts": ["verzoegert", "erschwert", "manipuliert", "kontrolliert", "beeinflusst", "drueckt Preise"],
        "counter_strategies": ["umgeht", "mildert", "passt sich an", "nutzt Netzwerke", "beschleunigt Verifizierung"],
        "enabling": ["ermoeglicht", "erleichtert", "unterstuetzt", "staerkt"],
        "causal": ["verursacht", "fuehrt zu", "resultiert in", "loest aus"]
    }
}
