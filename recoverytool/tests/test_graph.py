"""Unit tests for recoverytool.graph module."""
import pytest

from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver


def test_scene_graph():
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

    roots = graph.get_root_game_objects()
    assert len(roots) == 1
    assert roots[0] == go_obj
