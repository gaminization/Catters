"""Unit tests for recoverytool.generator modules."""
from pathlib import Path
import pytest

from recoverytool.database_builder import DatabaseBuilder
from recoverytool.editor.inspector_recovery import InspectorRecoveryEngine
from recoverytool.generator.editor_script_generator import EditorScriptGenerator
from recoverytool.generator.scene_reconstruction import ReconstructedGameObject, SceneReconstructionEngine
from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver


def test_generator_script(tmp_path):
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

    db_dir = tmp_path / "database"
    db_builder = DatabaseBuilder(db_dir)
    db_paths = db_builder.build_all(
        registry=registry,
        resolver=resolver,
        scene_graph=graph,
        asset_mapping={},
        reconstructed_roots=reconstructed_roots,
        validation_metrics_dict={},
    )

    inspector_engine = InspectorRecoveryEngine(tmp_path)
    output_cs = tmp_path / "RecoverScene.cs"

    generator = EditorScriptGenerator({}, inspector_engine, output_cs)
    code = generator.generate_from_scene_json(db_paths["scene"])

    assert "public static class RecoverScene" in code
    assert "ExecuteSceneRecovery" in code
    assert 'new GameObject("Canvas")' in code
    assert output_cs.exists()
