"""Unit tests for recoverytool.editor.validation module."""
from pathlib import Path
import pytest

from recoverytool.editor.validation import SceneValidator
from recoverytool.generator.scene_reconstruction import ReconstructedGameObject, SceneReconstructionEngine
from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver


def test_scene_validation(tmp_path):
    registry = PathIDRegistry()

    go_obj = UnityObject(
        path_id=40,
        class_id=1,
        type_name="GameObject",
        name="Canvas",
        properties={"m_Components": [{"m_FileID": 0, "m_PathID": 1572, "Name": "RectTransform"}]},
    )
    t_obj = UnityObject(
        path_id=1572,
        class_id=224,
        type_name="RectTransform",
        name="RectTransform",
        properties={"m_GameObject": {"m_FileID": 0, "m_PathID": 40}},
    )

    registry.register(go_obj)
    registry.register(t_obj)

    resolver = ReferenceResolver(registry)
    resolver.resolve_all()

    graph = SceneGraph()
    graph.build_from_registry(registry)

    recon_engine = SceneReconstructionEngine(graph)
    reconstructed_roots = recon_engine.build_reconstructed_tree()

    validator = SceneValidator(registry)
    metrics = validator.validate(reconstructed_roots)

    assert metrics.completeness_score_percent == 100.0
    report_file = tmp_path / "validation_report.md"
    validator.generate_validation_report(metrics, report_file)
    assert report_file.exists()
