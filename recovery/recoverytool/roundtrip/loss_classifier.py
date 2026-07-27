"""Loss Classifier module categorizing scene fidelity into 5 information tiers."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class LossTierSummary:
    tier: str
    count: int
    percentage: float
    description: str


class LossClassifier:
    """Classifies scene elements into 5 information loss tiers."""

    def __init__(self, registry: PathIDRegistry, asset_mapping: dict[int, dict[str, Any]]):
        self.registry = registry
        self.asset_mapping = asset_mapping

    def classify(self) -> list[LossTierSummary]:
        total_objects = len(self.registry.all_objects)
        if total_objects == 0:
            return []

        # Count by category
        raw_dump_recovered = 0
        inferred = 0
        matched = 0
        missing = 0
        impossible = 0

        for obj in self.registry.all_objects:
            if obj.type_name in ("GameObject", "Transform", "RectTransform", "MeshFilter", "BoxCollider"):
                raw_dump_recovered += 1
            elif obj.type_name in ("Mesh", "Material", "Texture2D", "Shader", "AnimatorController"):
                info = self.asset_mapping.get(obj.path_id, {})
                if info.get("matched"):
                    matched += 1
                else:
                    missing += 1
            elif obj.type_name == "MonoBehaviour":
                inferred += 1
            else:
                impossible += 1

        summaries = [
            LossTierSummary(
                tier="Recovered",
                count=raw_dump_recovered,
                percentage=round(raw_dump_recovered / total_objects * 100.0, 2),
                description="Exact data extracted directly from raw AssetStudio binary dump.",
            ),
            LossTierSummary(
                tier="Recovered by inference",
                count=inferred,
                percentage=round(inferred / total_objects * 100.0, 2),
                description="Deduced from scene tree relationships and component type signatures.",
            ),
            LossTierSummary(
                tier="Recovered by matching",
                count=matched,
                percentage=round(matched / total_objects * 100.0, 2),
                description="Matched by name & extension against ExportedProject .meta GUIDs.",
            ),
            LossTierSummary(
                tier="Missing",
                count=missing,
                percentage=round(missing / total_objects * 100.0, 2),
                description="Assets or references that could not be resolved or matched.",
            ),
            LossTierSummary(
                tier="Impossible to recover",
                count=impossible,
                percentage=round(impossible / total_objects * 100.0, 2),
                description="Stripped or compiled-out data not preserved in raw asset bundles.",
            ),
        ]

        return summaries

    def generate_report(self, output_md_path: Path | str) -> Path:
        summaries = self.classify()
        out_path = Path(output_md_path)

        lines = [
            "# Information Loss Classification Report",
            "",
            "Fidelity breakdown across the 5 information recovery tiers:",
            "",
            "| Information Loss Tier | Object Count | Percentage | Description |",
            "|---|---|---|---|",
        ]

        for s in summaries:
            lines.append(f"| **{s.tier}** | {s.count} | **{s.percentage}%** | {s.description} |")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
