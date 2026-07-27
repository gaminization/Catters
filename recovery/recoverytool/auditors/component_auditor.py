"""Component Auditor module verifying attached components against raw dump expectations."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class ComponentAuditItem:
    object_id: int
    object_name: str
    expected_components: list[str]
    recovered_components: list[str]
    missing_components: list[str]
    extra_components: list[str]
    passed: bool


class ComponentAuditor:
    """Verifies expected vs. recovered attached components per GameObject."""

    def __init__(self, registry: PathIDRegistry, scene_json_path: Path | str):
        self.registry = registry
        self.scene_json_path = Path(scene_json_path)
        self.audit_items: list[ComponentAuditItem] = []

    def audit(self) -> list[ComponentAuditItem]:
        self.audit_items.clear()
        if not self.scene_json_path.exists():
            return self.audit_items

        scene_data = json.loads(self.scene_json_path.read_text(encoding="utf-8"))
        roots = scene_data.get("root_objects", [])

        dumped_gos = {o.path_id: o for o in self.registry.all_objects if o.type_name == "GameObject"}

        def audit_node(node: dict[str, Any]):
            pid = node["path_id"]
            name = node["name"]

            raw_go = dumped_gos.get(pid)
            if raw_go:
                # Expected components
                expected_types: list[str] = []
                for comp_ref in raw_go.resolved_references.get("components", []):
                    expected_types.append(comp_ref.type_name)

                # Recovered components
                recovered_types = [c.get("type_name", "") for c in node.get("components", [])]

                missing = [t for t in expected_types if t not in recovered_types]
                extra = [t for t in recovered_types if t not in expected_types]
                passed = len(missing) == 0

                self.audit_items.append(
                    ComponentAuditItem(
                        object_id=pid,
                        object_name=name,
                        expected_components=expected_types,
                        recovered_components=recovered_types,
                        missing_components=missing,
                        extra_components=extra,
                        passed=passed,
                    )
                )

            for child in node.get("children", []):
                audit_node(child)

        for r in roots:
            audit_node(r)

        return self.audit_items

    def generate_report(self, output_md_path: Path | str) -> Path:
        out_path = Path(output_md_path)
        passed_count = sum(1 for i in self.audit_items if i.passed)
        total_count = len(self.audit_items)
        pass_rate = (passed_count / total_count * 100.0) if total_count > 0 else 100.0

        lines = [
            "# Component Verification Report",
            "",
            f"## Summary: **{passed_count} / {total_count} GameObjects Passed ({pass_rate:.2f}%)**",
            "",
            "| GameObject Name | PathID | Expected Components | Recovered Components | Missing Components | Status |",
            "|---|---|---|---|---|---|",
        ]

        for item in self.audit_items:
            status_str = "PASS" if item.passed else "WARN"
            exp_str = ", ".join(item.expected_components) if item.expected_components else "None"
            rec_str = ", ".join(item.recovered_components) if item.recovered_components else "None"
            miss_str = ", ".join(item.missing_components) if item.missing_components else "None"
            lines.append(
                f"| `{item.object_name}` | `{item.object_id}` | `{exp_str}` | `{rec_str}` | `{miss_str}` | **{status_str}** |"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
