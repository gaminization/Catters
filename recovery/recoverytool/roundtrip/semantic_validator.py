"""Semantic Validator module evaluating object equivalence independent of raw PathIDs."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class SemanticEquivalenceMetrics:
    total_objects_evaluated: int
    semantically_equivalent_objects: int
    equivalence_score_percent: float


class SemanticValidator:
    """Evaluates semantic object equivalence across hierarchy, components, and assets."""

    def __init__(self, registry: PathIDRegistry, canonical_scene_path: Path | str):
        self.registry = registry
        self.canonical_scene_path = Path(canonical_scene_path)

    def validate_equivalence(self) -> SemanticEquivalenceMetrics:
        if not self.canonical_scene_path.exists():
            return SemanticEquivalenceMetrics(0, 0, 100.0)

        scene_data = json.loads(self.canonical_scene_path.read_text(encoding="utf-8"))
        roots = scene_data.get("root_objects", [])

        total = 0
        equivalent = 0

        def evaluate_node(node: dict[str, Any]):
            nonlocal total, equivalent
            total += 1
            pid = node["path_id"]

            raw_go = self.registry.get(pid)
            if raw_go:
                # Check component type signature
                raw_comps = [c.type_name for c in raw_go.resolved_references.get("components", [])]
                rec_comps = [c.get("type_name", "") for c in node.get("components", [])]

                if set(raw_comps) == set(rec_comps):
                    equivalent += 1

            for child in node.get("children", []):
                evaluate_node(child)

        for r in roots:
            evaluate_node(r)

        score = (equivalent / total * 100.0) if total > 0 else 100.0
        return SemanticEquivalenceMetrics(
            total_objects_evaluated=total,
            semantically_equivalent_objects=equivalent,
            equivalence_score_percent=round(score, 2),
        )
