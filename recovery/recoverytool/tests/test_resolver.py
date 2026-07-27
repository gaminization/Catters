"""Unit tests for recoverytool.resolver modules."""
import pytest

from recoverytool.parser.base import PPtr, UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver


def test_registry_and_resolver():
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

    assert registry.get(40) == go_obj
    assert registry.get(1572) == t_obj

    resolver = ReferenceResolver(registry)
    resolver.resolve_all()

    assert "components" in go_obj.resolved_references
    assert len(go_obj.resolved_references["components"]) == 1
    assert go_obj.resolved_references["components"][0] == t_obj
