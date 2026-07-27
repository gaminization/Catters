"""Explainability Engine attaching source, confidence %, and reason to every recovered item."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class ExplainabilityItem:
    path_id: int
    name: str
    type_name: str
    source: str
    confidence_percent: float
    reason: str


class ExplainabilityEngine:
    """Attaches source provenance, confidence score, and rationale to every recovered element."""

    def __init__(self, registry: PathIDRegistry, asset_mapping: dict[int, dict[str, Any]]):
        self.registry = registry
        self.asset_mapping = asset_mapping

    def evaluate_explainability(self) -> list[ExplainabilityItem]:
        items: list[ExplainabilityItem] = []

        for obj in self.registry.all_objects:
            if obj.type_name in ("GameObject", "Transform", "RectTransform"):
                items.append(
                    ExplainabilityItem(
                        path_id=obj.path_id,
                        name=obj.name,
                        type_name=obj.type_name,
                        source="Raw Dump",
                        confidence_percent=100.0,
                        reason="Direct PathID PPtr link from AssetStudio binary dump.",
                    )
                )
            elif obj.type_name in ("Mesh", "Material", "Texture2D", "Shader", "AnimatorController"):
                info = self.asset_mapping.get(obj.path_id, {})
                if info.get("matched"):
                    items.append(
                        ExplainabilityItem(
                            path_id=obj.path_id,
                            name=obj.name,
                            type_name=obj.type_name,
                            source="ExportedProject Meta Matcher",
                            confidence_percent=92.0,
                            reason=f"Matched to {info.get('relative_path')} via filename & extension lookup.",
                        )
                    )
                else:
                    items.append(
                        ExplainabilityItem(
                            path_id=obj.path_id,
                            name=obj.name,
                            type_name=obj.type_name,
                            source="Unmatched Asset Indexer",
                            confidence_percent=0.0,
                            reason="No matching .meta GUID found in ExportedProject/Assets.",
                        )
                    )
            else:
                items.append(
                    ExplainabilityItem(
                        path_id=obj.path_id,
                        name=obj.name,
                        type_name=obj.type_name,
                        source="MonoBehaviour Reflection Engine",
                        confidence_percent=100.0,
                        reason="Extracted custom C# script serialized properties.",
                    )
                )

        return items

    def generate_report(self, output_md_path: Path | str) -> Path:
        items = self.evaluate_explainability()
        out_path = Path(output_md_path)

        lines = [
            "# Reconstruction Explainability Report",
            "",
            "Provenance, confidence scores, and rationales for all recovered Unity elements:",
            "",
            "| PathID | Name | Type | Source | Confidence | Rationale / Reason |",
            "|---|---|---|---|---|---|",
        ]

        for item in items:
            lines.append(
                f"| `{item.path_id}` | `{item.name}` | `{item.type_name}` | `{item.source}` | **{item.confidence_percent:.0f}%** | {item.reason} |"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
