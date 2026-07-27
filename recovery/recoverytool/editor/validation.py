"""Scene Recovery Validation Engine calculating scene completeness scores against raw dump."""
import logging
from dataclasses import dataclass
from pathlib import Path

from recoverytool.generator.scene_reconstruction import ReconstructedGameObject
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class ValidationMetrics:
    total_dumped_game_objects: int
    reconstructed_game_objects: int
    total_dumped_transforms: int
    reconstructed_transforms: int
    total_dumped_components: int
    reconstructed_components: int
    completeness_score_percent: float


class SceneValidator:
    """Validates reconstructed scene tree against raw dump registry."""

    def __init__(self, registry: PathIDRegistry):
        self.registry = registry

    def validate(self, reconstructed_roots: list[ReconstructedGameObject]) -> ValidationMetrics:
        """Calculates quantitative completeness score."""
        dumped_gos = [o for o in self.registry.all_objects if o.type_name == "GameObject"]
        dumped_transforms = [o for o in self.registry.all_objects if o.type_name in ("Transform", "RectTransform")]
        dumped_components = [
            o for o in self.registry.all_objects if o.type_name not in ("GameObject", "Transform", "RectTransform")
        ]

        reconstructed_go_ids: set[int] = set()
        reconstructed_comp_count = 0

        def traverse(node: ReconstructedGameObject):
            nonlocal reconstructed_comp_count
            reconstructed_go_ids.add(node.path_id)
            reconstructed_comp_count += len(node.components)
            for child in node.children:
                traverse(child)

        for root in reconstructed_roots:
            traverse(root)

        total_gos = len(dumped_gos)
        recon_gos = len(reconstructed_go_ids)

        go_score = (recon_gos / total_gos * 100.0) if total_gos > 0 else 100.0

        metrics = ValidationMetrics(
            total_dumped_game_objects=total_gos,
            reconstructed_game_objects=recon_gos,
            total_dumped_transforms=len(dumped_transforms),
            reconstructed_transforms=recon_gos,  # each reconstructed node has a transform
            total_dumped_components=len(dumped_components),
            reconstructed_components=reconstructed_comp_count,
            completeness_score_percent=round(go_score, 2),
        )

        return metrics

    def generate_validation_report(self, metrics: ValidationMetrics, report_path: Path) -> Path:
        """Generates markdown validation report."""
        lines = [
            "# Scene Recovery Validation Report",
            "",
            f"## Overall Completeness Score: **{metrics.completeness_score_percent}%**",
            "",
            "## Breakdown Metrics",
            "| Metric | Raw Dump Count | Reconstructed Count | Completeness |",
            "|---|---|---|---|",
            f"| GameObjects | {metrics.total_dumped_game_objects} | {metrics.reconstructed_game_objects} | {metrics.completeness_score_percent}% |",
            f"| Transforms | {metrics.total_dumped_transforms} | {metrics.reconstructed_transforms} | {metrics.completeness_score_percent}% |",
            f"| Attached Components | {metrics.total_dumped_components} | {metrics.reconstructed_components} | - |",
            "",
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path
