"""Database Builder module generating canonical JSON databases in recoverytool/database/."""
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from recoverytool.generator.scene_reconstruction import ReconstructedGameObject
from recoverytool.graph.scene_graph import SceneGraph
from recoverytool.parser.base import UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry
from recoverytool.resolver.reference_resolver import ReferenceResolver

logger = logging.getLogger(__name__)


class DatabaseBuilder:
    """Builds stable, deterministic JSON database files in database/."""

    def __init__(self, db_dir: Path | str):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)

    def build_all(
        self,
        registry: PathIDRegistry,
        resolver: ReferenceResolver,
        scene_graph: SceneGraph,
        asset_mapping: dict[int, dict[str, Any]],
        reconstructed_roots: list[ReconstructedGameObject],
        validation_metrics_dict: dict[str, Any],
    ) -> dict[str, Path]:
        """Generates all JSON database files."""
        paths: dict[str, Path] = {}

        # 1. objects.json
        objects_data = {}
        for obj in registry.all_objects:
            objects_data[str(obj.path_id)] = {
                "path_id": obj.path_id,
                "class_id": obj.class_id,
                "type_name": obj.type_name,
                "name": obj.name,
                "properties": obj.properties,
            }
        paths["objects"] = self._write_json("objects.json", objects_data)

        # 2. references.json
        references_data = {
            "total_objects": len(registry.all_objects),
            "broken_references_count": len(resolver.broken_references),
            "broken_references": [
                {
                    "source_path_id": b.source_path_id,
                    "source_type": b.source_type,
                    "target_path_id": b.target_path_id,
                    "field_name": b.field_name,
                }
                for b in resolver.broken_references
            ],
        }
        paths["references"] = self._write_json("references.json", references_data)

        # 3. graph.json
        graph_data = {
            "nodes": [
                {
                    "id": n,
                    "type_name": data.get("type_name", ""),
                    "name": data.get("name", ""),
                    "class_id": data.get("class_id", 0),
                }
                for n, data in scene_graph.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "key": k,
                    "rel_type": data.get("rel_type", ""),
                }
                for u, v, k, data in scene_graph.graph.edges(keys=True, data=True)
            ],
        }
        paths["graph"] = self._write_json("graph.json", graph_data)

        # 4. assets.json
        clean_assets_data = {str(k): v for k, v in asset_mapping.items()}
        paths["assets"] = self._write_json("assets.json", clean_assets_data)


        # 5. scene.json (canonical recovered scene)
        scene_tree = [self._serialize_node(r) for r in reconstructed_roots]
        canonical_scene_data = {
            "version": "1.0.0",
            "root_objects": scene_tree,
        }
        paths["scene"] = self._write_json("scene.json", canonical_scene_data)

        # 6. validation.json
        paths["validation"] = self._write_json("validation.json", validation_metrics_dict)

        return paths

    def _serialize_node(self, node: ReconstructedGameObject) -> dict[str, Any]:
        comp_list = []
        for comp in node.components:
            comp_list.append(
                {
                    "path_id": comp.path_id,
                    "type_name": comp.type_name,
                    "class_id": comp.class_id,
                    "name": comp.name,
                    "properties": comp.properties,
                }
            )

        t_props = node.transform_properties
        t_data = {}
        if t_props:
            pos = t_props.get("position")
            rot = t_props.get("rotation")
            scale = t_props.get("scale")
            t_data = {
                "position": {"x": pos.x, "y": pos.y, "z": pos.z} if pos else {},
                "rotation": {"x": rot.x, "y": rot.y, "z": rot.z, "w": rot.w} if rot else {},
                "scale": {"x": scale.x, "y": scale.y, "z": scale.z} if scale else {},
                "is_rect_transform": t_props.get("is_rect_transform", False),
            }

        return {
            "path_id": node.path_id,
            "name": node.name,
            "active": node.active,
            "layer": node.layer,
            "tag": node.tag,
            "transform": t_data,
            "components": comp_list,
            "children": [self._serialize_node(c) for c in node.children],
        }

    def _write_json(self, filename: str, data: Any) -> Path:
        p = self.db_dir / filename
        p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        return p
