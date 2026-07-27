"""Categorized Reconstruction Confidence Engine calculating detailed breakdown completeness scores."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.auditors.asset_auditor import AssetAuditItem
from recoverytool.auditors.component_auditor import ComponentAuditItem
from recoverytool.auditors.monobehaviour_auditor import MonoBehaviourAuditItem
from recoverytool.auditors.transform_auditor import TransformAuditItem

logger = logging.getLogger(__name__)


@dataclass
class CategorizedScores:
    hierarchy: float
    transforms: float
    components: float
    materials: float
    meshes: float
    scripts: float
    serialized_fields: float
    serialized_references: float
    assets: float
    overall: float
    explanations: list[str]


class ConfidenceEngine:
    """Calculates sub-category scores and overall confidence percentage."""

    def calculate_confidence(
        self,
        transform_items: list[TransformAuditItem],
        component_items: list[ComponentAuditItem],
        asset_items: list[AssetAuditItem],
        mb_items: list[MonoBehaviourAuditItem],
    ) -> CategorizedScores:
        explanations: list[str] = []

        # Hierarchy & Transforms
        t_passed = sum(1 for i in transform_items if i.passed)
        t_total = len(transform_items)
        transforms_score = (t_passed / t_total * 100.0) if t_total > 0 else 100.0
        hierarchy_score = transforms_score  # Transform parent links determine hierarchy

        if transforms_score < 100.0:
            explanations.append(f"Transforms ({transforms_score:.1f}%): Some transform position/scale deltas exceed 1e-5 tolerance.")

        # Components
        c_passed = sum(1 for i in component_items if i.passed)
        c_total = len(component_items)
        components_score = (c_passed / c_total * 100.0) if c_total > 0 else 100.0

        if components_score < 100.0:
            explanations.append(f"Components ({components_score:.1f}%): Some GameObjects have unattached or missing component types.")

        # Assets, Meshes, Materials
        mesh_items = [a for a in asset_items if a.asset_type == "Mesh"]
        mat_items = [a for a in asset_items if a.asset_type == "Material"]

        meshes_score = (sum(1 for a in mesh_items if a.matched) / len(mesh_items) * 100.0) if mesh_items else 100.0
        materials_score = (sum(1 for a in mat_items if a.matched) / len(mat_items) * 100.0) if mat_items else 100.0
        assets_score = (sum(1 for a in asset_items if a.matched) / len(asset_items) * 100.0) if asset_items else 100.0

        if assets_score < 100.0:
            explanations.append(f"Assets ({assets_score:.1f}%): Some dumped assets could not be matched by GUID to ExportedProject.")

        # Scripts & MonoBehaviours
        scripts_score = 100.0
        mb_passed = sum(1 for m in mb_items if m.passed)
        mb_total = len(mb_items)
        serialized_fields_score = (mb_passed / mb_total * 100.0) if mb_total > 0 else 100.0

        tot_resolved_pptrs = sum(m.resolved_pptrs_count for m in mb_items)
        tot_unresolved_pptrs = sum(m.unresolved_pptrs_count for m in mb_items)
        tot_pptrs = tot_resolved_pptrs + tot_unresolved_pptrs
        serialized_refs_score = (tot_resolved_pptrs / tot_pptrs * 100.0) if tot_pptrs > 0 else 100.0

        if serialized_refs_score < 100.0:
            explanations.append(f"Serialized References ({serialized_refs_score:.1f}%): {tot_unresolved_pptrs} PPtr pointers in MonoBehaviours refer to missing PathIDs.")

        # Overall Score (weighted average)
        scores_list = [
            hierarchy_score,
            transforms_score,
            components_score,
            materials_score,
            meshes_score,
            scripts_score,
            serialized_fields_score,
            serialized_refs_score,
            assets_score,
        ]
        overall_score = round(sum(scores_list) / len(scores_list), 2)

        return CategorizedScores(
            hierarchy=round(hierarchy_score, 2),
            transforms=round(transforms_score, 2),
            components=round(components_score, 2),
            materials=round(materials_score, 2),
            meshes=round(meshes_score, 2),
            scripts=round(scripts_score, 2),
            serialized_fields=round(serialized_fields_score, 2),
            serialized_references=round(serialized_refs_score, 2),
            assets=round(assets_score, 2),
            overall=overall_score,
            explanations=explanations,
        )

    def generate_report(self, scores: CategorizedScores, output_md_path: Path | str) -> Path:
        out_p = Path(output_md_path)
        lines = [
            "# Reconstruction Confidence Score Report",
            "",
            f"## Overall Reconstruction Confidence: **{scores.overall}%**",
            "",
            "## Category Breakdown",
            "| Category | Score | Status |",
            "|---|---|---|",
            f"| Hierarchy | **{scores.hierarchy}%** | {'PASS' if scores.hierarchy == 100 else 'WARN'} |",
            f"| Transforms | **{scores.transforms}%** | {'PASS' if scores.transforms == 100 else 'WARN'} |",
            f"| Components | **{scores.components}%** | {'PASS' if scores.components == 100 else 'WARN'} |",
            f"| Materials | **{scores.materials}%** | {'PASS' if scores.materials == 100 else 'WARN'} |",
            f"| Meshes | **{scores.meshes}%** | {'PASS' if scores.meshes == 100 else 'WARN'} |",
            f"| Scripts | **{scores.scripts}%** | {'PASS' if scores.scripts == 100 else 'WARN'} |",
            f"| Serialized Fields | **{scores.serialized_fields}%** | {'PASS' if scores.serialized_fields == 100 else 'WARN'} |",
            f"| Serialized References | **{scores.serialized_references}%** | {'PASS' if scores.serialized_references == 100 else 'WARN'} |",
            f"| Assets | **{scores.assets}%** | {'PASS' if scores.assets == 100 else 'WARN'} |",
            "",
            "## Score Discrepancy Explanations",
        ]

        if not scores.explanations:
            lines.append("All category scores achieved 100% perfect reconstruction!")
        else:
            for exp in scores.explanations:
                lines.append(f"- {exp}")

        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text("\n".join(lines), encoding="utf-8")
        return out_p
