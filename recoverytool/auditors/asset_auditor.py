"""Asset Auditor module verifying assets, GUIDs, relative paths, and confidence scores."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class AssetAuditItem:
    path_id: int
    name: str
    asset_type: str
    expected_path: str
    recovered_path: str
    guid: str
    confidence_score: float
    matched: bool


class AssetAuditor:
    """Verifies asset matching confidence and GUID resolution."""

    def __init__(self, registry: PathIDRegistry, asset_mapping: dict[int, dict[str, Any]]):
        self.registry = registry
        self.asset_mapping = asset_mapping
        self.audit_items: list[AssetAuditItem] = []

    def audit(self) -> list[AssetAuditItem]:
        self.audit_items.clear()

        for obj in self.registry.all_objects:
            if obj.type_name in (
                "Mesh",
                "Material",
                "Texture2D",
                "Sprite",
                "Font",
                "Shader",
                "AnimatorController",
                "Avatar",
                "AudioClip",
                "Prefab",
            ):
                mapping_info = self.asset_mapping.get(obj.path_id, {})
                matched = bool(mapping_info.get("matched", False))
                rel_path = str(mapping_info.get("relative_path", ""))
                guid = str(mapping_info.get("guid", ""))

                confidence = 1.0 if matched else 0.0

                self.audit_items.append(
                    AssetAuditItem(
                        path_id=obj.path_id,
                        name=obj.name,
                        asset_type=obj.type_name,
                        expected_path=rel_path or f"Assets/{obj.type_name}/{obj.name}",
                        recovered_path=rel_path,
                        guid=guid,
                        confidence_score=confidence,
                        matched=matched,
                    )
                )

        return self.audit_items

    def generate_report(self, output_md_path: Path | str) -> Path:
        out_path = Path(output_md_path)
        matched_count = sum(1 for i in self.audit_items if i.matched)
        total_count = len(self.audit_items)
        avg_confidence = (
            sum(i.confidence_score for i in self.audit_items) / total_count * 100.0 if total_count > 0 else 100.0
        )

        lines = [
            "# Asset Verification Report",
            "",
            f"## Summary: **{matched_count} / {total_count} Assets Matched ({avg_confidence:.2f}% Confidence)**",
            "",
            "| Asset Name | PathID | Type | GUID | Relative Path | Confidence | Status |",
            "|---|---|---|---|---|---|---|",
        ]

        for item in self.audit_items:
            status_str = "MATCHED" if item.matched else "UNMATCHED"
            conf_str = f"{item.confidence_score * 100:.0f}%"
            lines.append(
                f"| `{item.name}` | `{item.path_id}` | `{item.asset_type}` | `{item.guid}` | `{item.recovered_path}` | `{conf_str}` | **{status_str}** |"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
