"""Scene Reconstruction module organizing SceneGraph into hierarchical node trees."""
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.parser.object_parsers import UnityObjectParsers

logger = logging.getLogger(__name__)


@dataclass
class ReconstructedGameObject:
    game_object: UnityObject
    path_id: int
    name: str
    active: bool
    layer: int
    tag: str
    transform_properties: dict[str, Any] = field(default_factory=dict)
    components: list[UnityObject] = field(default_factory=list)
    children: list["ReconstructedGameObject"] = field(default_factory=list)


class SceneReconstructionEngine:
    """Infers structural hierarchy and reconstructs scene tree from SceneGraph."""

    def __init__(self, scene_graph: SceneGraph):
        self.graph = scene_graph

    def build_reconstructed_tree(self) -> list[ReconstructedGameObject]:
        """Builds tree of ReconstructedGameObjects starting from root GameObjects."""
        roots = self.graph.get_root_game_objects()
        reconstructed_roots: list[ReconstructedGameObject] = []

        for root_go in roots:
            reconstructed_roots.append(self._reconstruct_node(root_go))

        return reconstructed_roots

    def _reconstruct_node(self, go: UnityObject) -> ReconstructedGameObject:
        go_info = UnityObjectParsers.parse_game_object(go)

        # Get transform properties
        transform_obj = None
        for comp in go.resolved_references.get("components", []):
            if comp.type_name in ("Transform", "RectTransform"):
                transform_obj = comp
                break

        transform_props: dict[str, Any] = {}
        if transform_obj:
            transform_props = UnityObjectParsers.parse_transform(transform_obj)

        node = ReconstructedGameObject(
            game_object=go,
            path_id=go.path_id,
            name=go.name,
            active=go_info["active"],
            layer=go_info["layer"],
            tag=go_info["tag"],
            transform_properties=transform_props,
            components=go.resolved_references.get("components", []),
            children=[],
        )

        for child_go in self.graph.get_children(go):
            node.children.append(self._reconstruct_node(child_go))

        return node
