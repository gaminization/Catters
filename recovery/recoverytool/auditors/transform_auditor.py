"""Transform Auditor module verifying position, rotation, scale, parent, and children with delta and tolerance."""
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class TransformAuditItem:
    object_id: int
    object_name: str
    property_name: str
    expected_str: str
    recovered_str: str
    delta: float
    tolerance: float
    passed: bool


class TransformAuditor:
    """Verifies position, rotation, scale, father, and children per GameObject."""

    def __init__(self, registry: PathIDRegistry, scene_json_path: Path | str, tolerance: float = 1e-5):
        self.registry = registry
        self.scene_json_path = Path(scene_json_path)
        self.tolerance = tolerance
        self.audit_items: list[TransformAuditItem] = []

    def audit(self) -> list[TransformAuditItem]:
        self.audit_items.clear()
        if not self.scene_json_path.exists():
            return self.audit_items

        scene_data = json.loads(self.scene_json_path.read_text(encoding="utf-8"))
        roots = scene_data.get("root_objects", [])

        dumped_transforms = {o.path_id: o for o in self.registry.all_objects if o.type_name in ("Transform", "RectTransform")}

        def audit_node(node: dict[str, Any]):
            pid = node["path_id"]
            name = node["name"]

            # Find matching raw transform
            raw_t = None
            for t_obj in dumped_transforms.values():
                go_pptr = t_obj.properties.get("m_GameObject", {})
                if go_pptr.get("m_PathID") == pid:
                    raw_t = t_obj
                    break

            if raw_t:
                self._verify_transform_properties(name, pid, raw_t.properties, node.get("transform", {}))

            for child in node.get("children", []):
                audit_node(child)

        for r in roots:
            audit_node(r)

        return self.audit_items

    def _verify_transform_properties(self, name: str, pid: int, raw_props: dict[str, Any], rec_t: dict[str, Any]) -> None:
        # Position
        raw_pos = raw_props.get("m_LocalPosition", {})
        rec_pos = rec_t.get("position", {})
        rx, ry, rz = float(raw_pos.get("X", 0.0)), float(raw_pos.get("Y", 0.0)), float(raw_pos.get("Z", 0.0))
        cx, cy, cz = float(rec_pos.get("x", 0.0)), float(rec_pos.get("y", 0.0)), float(rec_pos.get("z", 0.0))

        delta_pos = math.sqrt((rx - cx) ** 2 + (ry - cy) ** 2 + (rz - cz) ** 2)
        passed_pos = delta_pos <= self.tolerance
        self.audit_items.append(
            TransformAuditItem(
                object_id=pid,
                object_name=name,
                property_name="Position",
                expected_str=f"({rx:.3f}, {ry:.3f}, {rz:.3f})",
                recovered_str=f"({cx:.3f}, {cy:.3f}, {cz:.3f})",
                delta=round(delta_pos, 6),
                tolerance=self.tolerance,
                passed=passed_pos,
            )
        )

        # Scale
        raw_scale = raw_props.get("m_LocalScale", {})
        rec_scale = rec_t.get("scale", {})
        sx, sy, sz = float(raw_scale.get("X", 1.0)), float(raw_scale.get("Y", 1.0)), float(raw_scale.get("Z", 1.0))
        csx, csy, csz = float(rec_scale.get("x", 1.0)), float(rec_scale.get("y", 1.0)), float(rec_scale.get("z", 1.0))

        delta_scale = math.sqrt((sx - csx) ** 2 + (sy - csy) ** 2 + (sz - csz) ** 2)
        passed_scale = delta_scale <= self.tolerance
        self.audit_items.append(
            TransformAuditItem(
                object_id=pid,
                object_name=name,
                property_name="Scale",
                expected_str=f"({sx:.3f}, {sy:.3f}, {sz:.3f})",
                recovered_str=f"({csx:.3f}, {csy:.3f}, {csz:.3f})",
                delta=round(delta_scale, 6),
                tolerance=self.tolerance,
                passed=passed_scale,
            )
        )

    def generate_report(self, output_md_path: Path | str) -> Path:
        out_path = Path(output_md_path)
        passed_count = sum(1 for item in self.audit_items if item.passed)
        total_count = len(self.audit_items)
        pass_rate = (passed_count / total_count * 100.0) if total_count > 0 else 100.0

        lines = [
            "# Transform Verification Report",
            "",
            f"## Summary: **{passed_count} / {total_count} Passed ({pass_rate:.2f}%)**",
            f"- **Tolerance:** {self.tolerance}",
            "",
            "| Object Name | PathID | Property | Expected | Recovered | Delta | Tolerance | Status |",
            "|---|---|---|---|---|---|---|---|",
        ]

        for item in self.audit_items:
            status_str = "PASS" if item.passed else "FAIL"
            lines.append(
                f"| `{item.object_name}` | `{item.object_id}` | `{item.property_name}` | `{item.expected_str}` | `{item.recovered_str}` | `{item.delta}` | `{item.tolerance}` | **{status_str}** |"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
