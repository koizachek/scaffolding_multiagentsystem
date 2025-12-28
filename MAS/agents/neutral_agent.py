"""
Neutraler Agent (Kontrollgruppe)

Dieser Agent gibt hilfreiche, aber lern-neutrale Hinweise zur Aufgabenbearbeitung.
Er fokussiert darauf, fehlende Pflichtkonzepte zu identifizieren und konkrete,
direkte Vorschläge zu machen, welche Knoten (und ggf. Beziehungen) ergänzt werden
sollten – ohne Scaffolding/Reflexionsfragen.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NeutralAgent:
    def __init__(self):
        self.name = "neutral"
        self.agent_type = "neutral"

    def generate_response(
        self,
        user_message: Optional[str] = None,
        concept_map: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        concepts = []
        relationships = []
        if isinstance(concept_map, dict):
            concepts = concept_map.get("concepts", []) or []
            relationships = concept_map.get("relationships", []) or []

        concept_labels = self._extract_concept_labels(concepts)
        normalized_map_text = self._normalize(" ".join(concept_labels))

        presence = self._detect_required_presence(normalized_map_text)
        missing = self._missing_labels(presence)

        mentioned_missing = []
        if user_message:
            mentioned_missing = self._mentioned_missing_in_message(user_message, presence)

        node_count = len(concepts) if isinstance(concepts, list) else 0
        edge_count = len(relationships) if isinstance(relationships, list) else 0

        header = f"Aktuell: {node_count} Konzepte, {edge_count} Beziehungen."

        if missing:
            lines = [header, "In deiner Concept Map fehlen noch folgende Pflichtkonzepte:"]
            lines.extend([f"- {label}" for label in missing])
            if mentioned_missing:
                lines.append(
                    "Du hast das bereits erwähnt – falls es noch nicht als Knoten in der Map steht, ergänze es: "
                    + ", ".join(mentioned_missing)
                    + "."
                )
            lines.append("Trage die fehlenden Punkte als Knoten ein und verbinde sie mit AMG.")
            return "\n".join(lines)

        # Optional: Hinweis auf Mindestanzahl an Verbindungen aus der Aufgabenbeschreibung
        if edge_count < 5:
            return (
                f"{header}\n"
                "Die Pflichtkonzepte sind vorhanden. Es fehlen aber noch Verbindungen (mindestens 5 insgesamt). "
                "Füge weitere beschriftete Pfeile hinzu, z. B. wie AMG Marktanalyse, Wettbewerbsumfeld, Ressourcen "
                "und Eintrittsstrategien beeinflusst."
            )

        return (
            f"{header}\n"
            "Die Pflichtkonzepte sind vorhanden. Du kannst jetzt die Beziehungen verfeinern (z. B. AMG → Ressourcen/Wettbewerb/Marktanalyse)."
        )

    def _extract_concept_labels(self, concepts: Any) -> List[str]:
        labels: List[str] = []
        if not isinstance(concepts, list):
            return labels

        for concept in concepts:
            label = None
            if isinstance(concept, dict):
                label = concept.get("text") or concept.get("label") or concept.get("id")
            elif isinstance(concept, str):
                label = concept

            if not label or not isinstance(label, str):
                continue

            # UUIDs/IDs vermeiden (typisch sehr lang und mit vielen "-")
            if "-" in label and len(label) > 30:
                continue

            labels.append(label.strip())

        return labels

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\säöüß-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _detect_required_presence(self, normalized_map_text: str) -> Dict[str, bool]:
        def has_any(keywords: List[str]) -> bool:
            return any(keyword in normalized_map_text for keyword in keywords)

        has_amg = has_any(["amg", "adaptive market gatekeeping", "gatekeeping", "adaptiv"])
        has_marktanalyse = has_any(
            [
                "marktanalyse",
                "marktforschung",
                "market analysis",
                "zielmarkt",
                "zielmärkt",
                "target market",
                "market research",
            ]
        )
        has_wettbewerb = has_any(
            [
                "wettbewerbsumfeld",
                "wettbewerb",
                "konkurrenz",
                "konkurrent",
                "rivalität",
                "competitive environment",
                "competition",
            ]
        )
        has_ressourcen = has_any(
            [
                "ressource",
                "kapital",
                "personal",
                "know-how",
                "knowhow",
                "finanzierung",
                "finanzen",
                "mitarbeit",
                "fachkräft",
                "expertise",
            ]
        )

        has_export = has_any(["export", "exportstrategie"])
        has_joint_venture = has_any(["joint venture", "jointventure", "jv"])
        has_direktinvestition = has_any(
            [
                "direktinvest",
                "direktinvestment",
                "direct investment",
                "fdi",
                "tochtergesellschaft",
                "niederlassung",
            ]
        )

        has_any_entry_strategy = has_export or has_joint_venture or has_direktinvestition or has_any(
            ["eintrittsstrateg", "markteintrittsstrateg", "eintrittsstrategie"]
        )

        return {
            "amg": has_amg,
            "marktanalyse": has_marktanalyse,
            "wettbewerbsumfeld": has_wettbewerb,
            "ressourcen": has_ressourcen,
            "eintrittsstrategien": has_any_entry_strategy,
            "export": has_export,
            "joint_venture": has_joint_venture,
            "direktinvestition": has_direktinvestition,
        }

    def _missing_labels(self, presence: Dict[str, bool]) -> List[str]:
        missing: List[str] = []

        if not presence.get("amg", False):
            missing.append("AMG (Adaptive Market Gatekeeping)")
        if not presence.get("marktanalyse", False):
            missing.append("Marktanalyse")
        if not presence.get("wettbewerbsumfeld", False):
            missing.append("Wettbewerbsumfeld")
        if not presence.get("ressourcen", False):
            missing.append("Ressourcen (Kapital, Personal, Know-how)")

        if not presence.get("eintrittsstrategien", False):
            missing.append("Eintrittsstrategien (Export / Joint Venture / Direktinvestition)")
            return missing

        if not presence.get("export", False):
            missing.append("Export")
        if not presence.get("joint_venture", False):
            missing.append("Joint Venture")
        if not presence.get("direktinvestition", False):
            missing.append("Direktinvestition")

        return missing

    def _mentioned_missing_in_message(self, user_message: str, presence: Dict[str, bool]) -> List[str]:
        normalized_message = self._normalize(user_message)

        def msg_has_any(keywords: List[str]) -> bool:
            return any(keyword in normalized_message for keyword in keywords)

        mentioned: List[str] = []

        if not presence.get("marktanalyse", False) and msg_has_any(["marktanalyse", "marktforschung", "zielmarkt"]):
            mentioned.append("Marktanalyse")
        if not presence.get("wettbewerbsumfeld", False) and msg_has_any(["wettbewerb", "konkurrenz", "konkurrent"]):
            mentioned.append("Wettbewerbsumfeld")
        if not presence.get("ressourcen", False) and msg_has_any(["ressource", "kapital", "personal", "know", "finanz"]):
            mentioned.append("Ressourcen")
        if not presence.get("export", False) and msg_has_any(["export"]):
            mentioned.append("Export")
        if not presence.get("joint_venture", False) and msg_has_any(["joint venture", "jv"]):
            mentioned.append("Joint Venture")
        if not presence.get("direktinvestition", False) and msg_has_any(["direktinvest", "tochtergesellschaft", "niederlassung"]):
            mentioned.append("Direktinvestition")
        if not presence.get("amg", False) and msg_has_any(["amg", "gatekeeping"]):
            mentioned.append("AMG")

        return mentioned
