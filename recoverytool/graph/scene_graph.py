"""SceneGraph module built on networkx.MultiDiGraph for Unity scene traversal and relationship modeling."""
import logging
from typing import Any, Optional

import networkx as nx

from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)

# Edge relationship types
EDGE_PARENT_OF = "PARENT_OF"
EDGE_HAS_COMPONENT = "HAS_COMPONENT"
EDGE_USES_ASSET = "USES_ASSET"
EDGE_DEPENDS_ON = "DEPENDS_ON"
EDGE_REFERENCES = "REFERENCES"
EDGE_USES_SCRIPT = "USES_SCRIPT"
EDGE_USES_MATERIAL = "USES_MATERIAL"
EDGE_USES_TEXTURE = "USES_TEXTURE"
EDGE_USES_MESH = "USES_MESH"


class SceneGraph:
    """Scene graph implementation wrapping a networkx.MultiDiGraph with AssetKey node identity."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._objects_by_key: dict[str, UnityObject] = {}
        self._objects_by_path_id: dict[int, UnityObject] = {}

    def add_object_node(self, obj: UnityObject) -> None:
        key_str = str(obj.key)
        self._objects_by_key[key_str] = obj
        if obj.path_id not in self._objects_by_path_id or obj.asset_file == "level0":
            self._objects_by_path_id[obj.path_id] = obj

        self.graph.add_node(
            key_str,
            path_id=obj.path_id,
            asset_file=obj.asset_file,
            type_name=obj.type_name,
            class_id=obj.class_id,
            name=obj.name,
            unity_obj=obj,
        )

    def add_relationship(self, source_obj: UnityObject, target_obj: UnityObject, rel_type: str) -> None:
        sk = str(source_obj.key)
        tk = str(target_obj.key)
        if sk in self.graph and tk in self.graph:
            self.graph.add_edge(sk, tk, rel_type=rel_type)

    def build_from_registry(self, registry: PathIDRegistry) -> None:
        """Populates graph nodes and MultiDiGraph edges from resolved registry."""
        for obj in registry.all_objects:
            self.add_object_node(obj)

        for obj in registry.all_objects:
            # GameObject -> Components
            if obj.type_name == "GameObject":
                components = obj.resolved_references.get("components", [])
                for comp in components:
                    self.add_relationship(obj, comp, EDGE_HAS_COMPONENT)

            # Transform hierarchy
            if obj.type_name in ("Transform", "RectTransform"):
                father = obj.resolved_references.get("father")
                if father:
                    self.add_relationship(father, obj, EDGE_PARENT_OF)

                go = obj.resolved_references.get("m_GameObject")
                if go:
                    self.add_relationship(obj, go, EDGE_HAS_COMPONENT)

            # Component -> Assets
            if obj.type_name == "MeshFilter":
                mesh = obj.resolved_references.get("mesh")
                if mesh:
                    self.add_relationship(obj, mesh, EDGE_USES_MESH)

            if obj.type_name in ("MeshRenderer", "SkinnedMeshRenderer"):
                materials = obj.resolved_references.get("materials", [])
                for mat in materials:
                    self.add_relationship(obj, mat, EDGE_USES_MATERIAL)

            if obj.type_name == "MonoBehaviour":
                script = obj.resolved_references.get("script")
                if script:
                    self.add_relationship(obj, script, EDGE_USES_SCRIPT)

    def get_object(self, path_id: int) -> Optional[UnityObject]:
        return self._objects_by_path_id.get(path_id)

    def get_root_game_objects(self) -> list[UnityObject]:
        """Returns all root GameObjects belonging to the scene stream (level0)."""
        roots: list[UnityObject] = []
        for key_str, data in self.graph.nodes(data=True):
            obj: UnityObject = data.get("unity_obj")
            if obj and obj.type_name == "GameObject" and obj.asset_file == "level0":
                transform = None
                for comp in obj.resolved_references.get("components", []):
                    if comp.type_name in ("Transform", "RectTransform"):
                        transform = comp
                        break
                if transform is None or transform.resolved_references.get("father") is None:
                    roots.append(obj)
        return roots

    def get_children(self, game_object: UnityObject) -> list[UnityObject]:
        """Returns list of child GameObjects."""
        transform = self._get_transform(game_object)
        if not transform:
            return []
        child_transforms = transform.resolved_references.get("children", [])
        child_gos: list[UnityObject] = []
        for ct in child_transforms:
            go = ct.resolved_references.get("m_GameObject")
            if go:
                child_gos.append(go)
        return child_gos

    def get_components(self, game_object: UnityObject) -> list[UnityObject]:
        return game_object.resolved_references.get("components", [])

    def _get_transform(self, game_object: UnityObject) -> Optional[UnityObject]:
        for comp in game_object.resolved_references.get("components", []):
            if comp.type_name in ("Transform", "RectTransform"):
                return comp
        return None
