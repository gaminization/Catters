"""Unit tests for Phase 11 auditors, database builder, scene diff, and confidence engine."""
from pathlib import Path
import pytest

from recoverytool.auditors.asset_auditor import AssetAuditor
from recoverytool.auditors.component_auditor import ComponentAuditor
from recoverytool.auditors.monobehaviour_auditor import MonoBehaviourAuditor
from recoverytool.auditors.transform_auditor import TransformAuditor
from recoverytool.confidence_engine import ConfidenceEngine
from recoverytool.database_builder import DatabaseBuilder
from recoverytool.editor.inspector_recovery import InspectorRecoveryEngine
from recoverytool.generator.scene_reconstruction import SceneReconstructionEngine
from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver
from recoverytool.scene_diff import SceneDiffEngine


def test_phase11_audit_pipeline(tmp_path):
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

    scene_graph = SceneGraph()
    scene_graph.build_from_registry(registry)

    recon_engine = SceneReconstructionEngine(scene_graph)
    reconstructed_roots = recon_engine.build_reconstructed_tree()

    db_dir = tmp_path / "database"
    db_builder = DatabaseBuilder(db_dir)
    db_paths = db_builder.build_all(
        registry=registry,
        resolver=resolver,
        scene_graph=scene_graph,
        asset_mapping={},
        reconstructed_roots=reconstructed_roots,
        validation_metrics_dict={},
    )

    assert db_paths["scene"].exists()
    assert db_paths["objects"].exists()
    assert db_paths["references"].exists()
    assert db_paths["graph"].exists()
    assert db_paths["assets"].exists()

    # Diff engine
    diff_engine = SceneDiffEngine(registry, db_paths["scene"])
    diffs = diff_engine.compute_diff()
    assert isinstance(diffs, list)

    # Transform auditor
    t_auditor = TransformAuditor(registry, db_paths["scene"])
    t_items = t_auditor.audit()
    assert isinstance(t_items, list)

    # Component auditor
    c_auditor = ComponentAuditor(registry, db_paths["scene"])
    c_items = c_auditor.audit()
    assert len(c_items) == 1
    assert c_items[0].passed

    # Confidence engine
    conf_engine = ConfidenceEngine()
    scores = conf_engine.calculate_confidence(t_items, c_items, [], [])
    assert scores.overall >= 0.0
