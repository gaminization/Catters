"""Scene Diff Engine comparing raw AssetStudio dump against canonical recovered scene database."""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class DiffItem:
    category: str
    object_id: int
    object_name: str
    description: str
    expected: Any
    actual: Any


class SceneDiffEngine:
    """Full Scene Diff Engine comparing raw dump vs. canonical database/scene.json."""

    def __init__(self, registry: PathIDRegistry, scene_json_path: Path | str):
        self.registry = registry
        self.scene_json_path = Path(scene_json_path)
        self.diffs: list[DiffItem] = []

    def compute_diff(self) -> list[DiffItem]:
        """Computes comprehensive diff items across all Unity scene aspects."""
        self.diffs.clear()

        if not self.scene_json_path.exists():
            logger.warning(f"scene.json path does not exist: {self.scene_json_path}")
            return self.diffs

        scene_data = json.loads(self.scene_json_path.read_text(encoding="utf-8"))
        recovered_tree = scene_data.get("root_objects", [])

        # Collect raw objects
        dumped_gos = {o.path_id: o for o in self.registry.all_objects if o.type_name == "GameObject"}

        # Collect recovered objects
        recovered_gos: dict[int, dict[str, Any]] = {}

        def index_nodes(node: dict[str, Any]):
            recovered_gos[node["path_id"]] = node
            for child in node.get("children", []):
                index_nodes(child)

        for root in recovered_tree:
            index_nodes(root)

        # 1. Missing / Extra GameObjects
        for pid, raw_go in dumped_gos.items():
            if pid not in recovered_gos:
                self.diffs.append(
                    DiffItem(
                        category="Missing GameObject",
                        object_id=pid,
                        object_name=raw_go.name,
                        description=f"GameObject {raw_go.name} (PathID: {pid}) present in raw dump but missing in scene.json.",
                        expected=f"GameObject {raw_go.name}",
                        actual="Missing",
                    )
                )

        for pid, rec_go in recovered_gos.items():
            if pid not in dumped_gos:
                self.diffs.append(
                    DiffItem(
                        category="Extra GameObject",
                        object_id=pid,
                        object_name=rec_go["name"],
                        description=f"GameObject {rec_go['name']} (PathID: {pid}) present in scene.json but missing in raw dump.",
                        expected="Missing",
                        actual=f"GameObject {rec_go['name']}",
                    )
                )

        # 2. Property & Component Mismatches for matched GameObjects
        for pid, raw_go in dumped_gos.items():
            if pid in recovered_gos:
                rec_go = recovered_gos[pid]
                self._diff_gameobject(raw_go, rec_go)

        return self.diffs

    def _diff_gameobject(self, raw_go: UnityObject, rec_go: dict[str, Any]) -> None:
        raw_props = raw_go.properties

        # Tag mismatch
        raw_tag = str(raw_props.get("m_Tag", "Untagged"))
        rec_tag = rec_go.get("tag", "Untagged")
        if raw_tag != rec_tag:
            self.diffs.append(
                DiffItem(
                    category="Tag Mismatch",
                    object_id=raw_go.path_id,
                    object_name=raw_go.name,
                    description=f"Tag mismatch for {raw_go.name}",
                    expected=raw_tag,
                    actual=rec_tag,
                )
            )

        # Layer mismatch
        raw_layer = int(raw_props.get("m_Layer", 0))
        rec_layer = rec_go.get("layer", 0)
        if raw_layer != rec_layer:
            self.diffs.append(
                DiffItem(
                    category="Layer Mismatch",
                    object_id=raw_go.path_id,
                    object_name=raw_go.name,
                    description=f"Layer mismatch for {raw_go.name}",
                    expected=raw_layer,
                    actual=rec_layer,
                )
            )

        # Active state mismatch
        raw_active = bool(raw_props.get("m_IsActive", True))
        rec_active = bool(rec_go.get("active", True))
        if raw_active != rec_active:
            self.diffs.append(
                DiffItem(
                    category="Active State Mismatch",
                    object_id=raw_go.path_id,
                    object_name=raw_go.name,
                    description=f"Active state mismatch for {raw_go.name}",
                    expected=raw_active,
                    actual=rec_active,
                )
            )

    def generate_report(self, output_md_path: Path | str) -> Path:
        """Writes scene_diff.md report."""
        out_path = Path(output_md_path)
        lines = [
            "# Full Scene Diff Report",
            "",
            f"Total Diff Discrepancies Found: **{len(self.diffs)}**",
            "",
            "| Category | Object Name | PathID | Description | Expected | Actual |",
            "|---|---|---|---|---|---|",
        ]

        if not self.diffs:
            lines.append("| Clean | None | 0 | Full match with zero discrepancies! | - | - |")
        else:
            for item in self.diffs:
                lines.append(
                    f"| `{item.category}` | `{item.object_name}` | `{item.object_id}` | {item.description} | `{item.expected}` | `{item.actual}` |"
                )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
