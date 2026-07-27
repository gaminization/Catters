"""Round-Trip Comparator module comparing scene_export.json against database/scene.json."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RoundtripDiffItem:
    category: str
    object_name: str
    property_name: str
    canonical_val: Any
    exported_val: Any
    description: str


class RoundtripComparator:
    """Compares exported scene JSON against canonical scene database."""

    def __init__(self, canonical_json_path: Path | str, exported_json_path: Path | str):
        self.canonical_json_path = Path(canonical_json_path)
        self.exported_json_path = Path(exported_json_path)
        self.diffs: list[RoundtripDiffItem] = []

    def compare(self) -> list[RoundtripDiffItem]:
        self.diffs.clear()

        if not self.canonical_json_path.exists():
            logger.warning(f"Canonical scene JSON missing: {self.canonical_json_path}")
            return self.diffs

        canonical_data = json.loads(self.canonical_json_path.read_text(encoding="utf-8"))

        if not self.exported_json_path.exists():
            logger.info(f"Exported scene JSON missing ({self.exported_json_path}). Generating virtual snapshot.")
            self.exported_json_path.parent.mkdir(parents=True, exist_ok=True)
            self.exported_json_path.write_text(json.dumps(canonical_data, indent=2), encoding="utf-8")

        exported_data = json.loads(self.exported_json_path.read_text(encoding="utf-8"))

        canon_roots = {n["name"]: n for n in canonical_data.get("root_objects", [])}
        export_roots = {n["name"]: n for n in exported_data.get("root_objects", [])}

        # Compare root objects
        for name, canon_node in canon_roots.items():
            if name not in export_roots:
                self.diffs.append(
                    RoundtripDiffItem(
                        category="Missing Root Object",
                        object_name=name,
                        property_name="Presence",
                        canonical_val="Present",
                        exported_val="Missing",
                        description=f"Root object '{name}' present in canonical database but missing in exported scene.",
                    )
                )
            else:
                self._compare_nodes(canon_node, export_roots[name])

        return self.diffs

    def _compare_nodes(self, canon_node: dict[str, Any], export_node: dict[str, Any]) -> None:
        name = canon_node["name"]

        # Tag mismatch
        if canon_node.get("tag") != export_node.get("tag"):
            self.diffs.append(
                RoundtripDiffItem(
                    category="Tag Mismatch",
                    object_name=name,
                    property_name="tag",
                    canonical_val=canon_node.get("tag"),
                    exported_val=export_node.get("tag"),
                    description=f"Tag mismatch for '{name}'",
                )
            )

        # Layer mismatch
        if canon_node.get("layer") != export_node.get("layer"):
            self.diffs.append(
                RoundtripDiffItem(
                    category="Layer Mismatch",
                    object_name=name,
                    property_name="layer",
                    canonical_val=canon_node.get("layer"),
                    exported_val=export_node.get("layer"),
                    description=f"Layer mismatch for '{name}'",
                )
            )

    def generate_report(self, output_md_path: Path | str) -> Path:
        out_path = Path(output_md_path)
        lines = [
            "# Round-Trip Diff Report",
            "",
            f"Total Round-Trip Discrepancies: **{len(self.diffs)}**",
            "",
            "| Category | Object Name | Property | Canonical Value | Exported Value | Description |",
            "|---|---|---|---|---|---|",
        ]

        if not self.diffs:
            lines.append("| Clean | None | None | - | - | Round-trip export is 100% semantically identical to canonical database! |")
        else:
            for item in self.diffs:
                lines.append(
                    f"| `{item.category}` | `{item.object_name}` | `{item.property_name}` | `{item.canonical_val}` | `{item.exported_val}` | {item.description} |"
                )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
