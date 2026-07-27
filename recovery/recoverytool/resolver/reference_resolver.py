"""Reference Resolver module connecting raw PPtr PathIDs to in-memory UnityObject references."""
import logging
from dataclasses import dataclass
from typing import Any, Optional

from recoverytool.parser.base import PPtr, UnityObject
from recoverytool.resolver.pathid_registry import PathIDRegistry

logger = logging.getLogger(__name__)


@dataclass
class BrokenReference:
    source_path_id: int
    source_type: str
    target_path_id: int
    field_name: str


class ReferenceResolver:
    """Resolves PPtr references into direct in-memory object references."""

    def __init__(self, registry: PathIDRegistry):
        self.registry = registry
        self.broken_references: list[BrokenReference] = []

    def resolve_pptr(self, pptr: PPtr, source_obj: UnityObject, field_name: str) -> Optional[UnityObject]:
        if pptr.is_null or pptr.path_id == 0:
            return None
        target = self.registry.get(pptr.path_id)
        if target is None:
            self.broken_references.append(
                BrokenReference(
                    source_path_id=source_obj.path_id,
                    source_type=source_obj.type_name,
                    target_path_id=pptr.path_id,
                    field_name=field_name,
                )
            )
        return target

    def resolve_all(self) -> None:
        """Traverses all registered objects and populates resolved_references."""
        for obj in self.registry.all_objects:
            resolved: dict[str, Any] = {}

            # Generic reference resolution
            for idx, ref in enumerate(obj.references):
                key = f"ref_{idx}_{ref.path_id}"
                resolved_target = self.resolve_pptr(ref, obj, key)
                if resolved_target:
                    resolved[key] = resolved_target

            # GameObject component resolution (handles m_Components and m_Component)
            if obj.type_name == "GameObject":
                components: list[UnityObject] = []
                comp_raw_list = obj.properties.get("m_Component", obj.properties.get("m_Components", []))
                for comp_pptr in extract_pptr_list(comp_raw_list):
                    comp_obj = self.resolve_pptr(comp_pptr, obj, "m_Components")
                    if comp_obj:
                        components.append(comp_obj)
                        # Back link component -> GameObject
                        comp_obj.resolved_references["m_GameObject"] = obj
                resolved["components"] = components

            # Transform father/children resolution
            if obj.type_name in ("Transform", "RectTransform"):
                father_pptr = PPtr.from_dict(obj.properties.get("m_Father"))
                father_obj = self.resolve_pptr(father_pptr, obj, "m_Father")
                if father_obj:
                    resolved["father"] = father_obj

                children: list[UnityObject] = []
                for child_pptr in extract_pptr_list(obj.properties.get("m_Children", [])):
                    child_obj = self.resolve_pptr(child_pptr, obj, "m_Children")
                    if child_obj:
                        children.append(child_obj)
                resolved["children"] = children

            # MeshFilter mesh resolution
            if obj.type_name == "MeshFilter":
                mesh_pptr = PPtr.from_dict(obj.properties.get("m_Mesh"))
                mesh_obj = self.resolve_pptr(mesh_pptr, obj, "m_Mesh")
                if mesh_obj:
                    resolved["mesh"] = mesh_obj

            # MeshRenderer materials resolution
            if obj.type_name in ("MeshRenderer", "SkinnedMeshRenderer"):
                materials: list[UnityObject] = []
                for mat_pptr in extract_pptr_list(obj.properties.get("m_Materials", [])):
                    mat_obj = self.resolve_pptr(mat_pptr, obj, "m_Materials")
                    if mat_obj:
                        materials.append(mat_obj)
                resolved["materials"] = materials

            # MonoBehaviour script resolution
            if obj.type_name == "MonoBehaviour":
                script_pptr = PPtr.from_dict(obj.properties.get("m_Script"))
                script_obj = self.resolve_pptr(script_pptr, obj, "m_Script")
                if script_obj:
                    resolved["script"] = script_obj

            obj.resolved_references.update(resolved)


def extract_pptr_list(items: Any) -> list[PPtr]:
    res: list[PPtr] = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                if "component" in item and isinstance(item["component"], dict):
                    res.append(PPtr.from_dict(item["component"]))
                else:
                    res.append(PPtr.from_dict(item))
    return res
