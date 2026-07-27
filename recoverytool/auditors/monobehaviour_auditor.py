"""MonoBehaviour Auditor module verifying custom serialized fields and PPtr references."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.editor.inspector_recovery import InspectorRecoveryEngine
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class MonoBehaviourAuditItem:
    path_id: int
    script_name: str
    game_object_name: str
    field_count: int
    resolved_pptrs_count: int
    unresolved_pptrs_count: int
    passed: bool


class MonoBehaviourAuditor:
    """Verifies custom MonoBehaviour field serialization and PPtr resolution."""

    def __init__(self, registry: PathIDRegistry, inspector_engine: InspectorRecoveryEngine):
        self.registry = registry
        self.inspector_engine = inspector_engine
        self.audit_items: list[MonoBehaviourAuditItem] = []

    def audit(self) -> list[MonoBehaviourAuditItem]:
        self.audit_items.clear()

        mbs = [o for o in self.registry.all_objects if o.type_name == "MonoBehaviour"]

        for mb in mbs:
            script_pptr = mb.resolved_references.get("script")
            script_name = script_pptr.name if script_pptr else "UnknownScript"
            go_obj = mb.resolved_references.get("m_GameObject")
            go_name = go_obj.name if go_obj else "UnknownGO"

            # Count custom non-standard fields
            standard_keys = {
                "m_GameObject",
                "m_Enabled",
                "m_Script",
                "m_Name",
                "type",
                "classID",
                "m_PathID",
                "byteSize",
            }
            custom_fields = {k: v for k, v in mb.properties.items() if k not in standard_keys}

            # Check PPtr references inside MonoBehaviour
            resolved_pptrs = 0
            unresolved_pptrs = 0

            for ref in mb.references:
                if ref.path_id != 0:
                    if self.registry.contains(ref.path_id):
                        resolved_pptrs += 1
                    else:
                        unresolved_pptrs += 1

            passed = unresolved_pptrs == 0

            self.audit_items.append(
                MonoBehaviourAuditItem(
                    path_id=mb.path_id,
                    script_name=script_name,
                    game_object_name=go_name,
                    field_count=len(custom_fields),
                    resolved_pptrs_count=resolved_pptrs,
                    unresolved_pptrs_count=unresolved_pptrs,
                    passed=passed,
                )
            )

        return self.audit_items

    def generate_report(self, output_md_path: Path | str) -> Path:
        out_path = Path(output_md_path)
        passed_count = sum(1 for i in self.audit_items if i.passed)
        total_count = len(self.audit_items)
        pass_rate = (passed_count / total_count * 100.0) if total_count > 0 else 100.0

        lines = [
            "# MonoBehaviour Verification Report",
            "",
            f"## Summary: **{passed_count} / {total_count} MonoBehaviours Passed ({pass_rate:.2f}%)**",
            "",
            "| Script Name | GameObject Name | PathID | Custom Fields | Resolved PPtrs | Unresolved PPtrs | Status |",
            "|---|---|---|---|---|---|---|",
        ]

        for item in self.audit_items:
            status_str = "PASS" if item.passed else "WARN"
            lines.append(
                f"| `{item.script_name}` | `{item.game_object_name}` | `{item.path_id}` | {item.field_count} | {item.resolved_pptrs_count} | {item.unresolved_pptrs_count} | **{status_str}** |"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path
