"""Editor Script Generator module rendering compilable C# Unity Editor RecoverScene.cs directly from database/scene.json."""
import json
import logging
import re
from pathlib import Path
from typing import Any

from recoverytool.editor.inspector_recovery import InspectorRecoveryEngine

logger = logging.getLogger(__name__)

# Known built-in Unity component type names mapped to their full C# type name
BUILTIN_COMPONENT_TYPES = {
    "CanvasRenderer": "CanvasRenderer",
    "Light": "Light",
    "AudioSource": "AudioSource",
    "BoxCollider": "BoxCollider",
    "SphereCollider": "SphereCollider",
    "CapsuleCollider": "CapsuleCollider",
    "MeshFilter": "MeshFilter",
    "MeshRenderer": "MeshRenderer",
    "SkinnedMeshRenderer": "SkinnedMeshRenderer",
    "MeshCollider": "MeshCollider",
    "Animator": "Animator",
    "Camera": "Camera",
    "Canvas": "Canvas",
    "RectTransform": "RectTransform",
}

# Optional package / UI component type mappings with assembly candidates
PACKAGE_OPTIONAL_TYPES = {
    "CanvasScaler": "UnityEngine.UI.CanvasScaler",
    "GraphicRaycaster": "UnityEngine.UI.GraphicRaycaster",
    "Image": "UnityEngine.UI.Image",
    "RawImage": "UnityEngine.UI.RawImage",
    "Text": "UnityEngine.UI.Text",
    "Button": "UnityEngine.UI.Button",
    "Toggle": "UnityEngine.UI.Toggle",
    "Slider": "UnityEngine.UI.Slider",
    "Scrollbar": "UnityEngine.UI.Scrollbar",
    "Dropdown": "UnityEngine.UI.Dropdown",
    "InputField": "UnityEngine.UI.InputField",
    "EventSystem": "UnityEngine.EventSystems.EventSystem",
    "StandaloneInputModule": "UnityEngine.EventSystems.StandaloneInputModule",
    "TextMeshProUGUI": "TMPro.TextMeshProUGUI",
    "TextMeshPro": "TMPro.TextMeshPro",
    "TMP_Text": "TMPro.TMP_Text",
}


def resolve_unity_tag(tag_val: Any, custom_tags: list[str] | None = None) -> str | None:
    """Resolves Unity numeric tag IDs or raw strings to canonical Unity tag names."""
    if custom_tags is None:
        custom_tags = ["Obstacle"]
    if tag_val is None or tag_val == "" or tag_val == "Untagged":
        return None
    try:
        tag_id = int(tag_val)
    except (ValueError, TypeError):
        return tag_val if tag_val not in ("0", "Untagged") else None

    builtin_tags = {
        0: None,
        1: "Respawn",
        2: "Finish",
        3: "EditorOnly",
        4: "MainCamera",
        5: "MainCamera",
        6: "Player",
        7: "GameController",
    }
    if tag_id in builtin_tags:
        return builtin_tags[tag_id]
    if tag_id >= 20000:
        idx = tag_id - 20000
        if 0 <= idx < len(custom_tags):
            return custom_tags[idx]
    return None


class EditorScriptGenerator:
    """Renders compilable C# Unity Editor script for scene reconstruction directly from database/scene.json."""

    def __init__(
        self,
        asset_mapping: dict[Any, dict[str, Any]],
        inspector_engine: InspectorRecoveryEngine,
        output_cs_path: Path | str,
    ):
        self.asset_mapping = asset_mapping
        self.inspector_engine = inspector_engine
        self.output_cs_path = Path(output_cs_path)

    def resolve_asset_info(self, pptr: dict[str, Any]) -> dict[str, Any] | None:
        """Resolves PPtr to asset info using composite AssetKeys."""
        if not isinstance(pptr, dict):
            return None
        fid = pptr.get("m_FileID", 0)
        pid = pptr.get("m_PathID", 0)
        if not pid:
            return None

        file_table = {
            0: "level0",
            1: "globalgamemanagers.assets",
            2: "sharedassets0.assets",
            3: "resources.assets",
        }
        af_name = file_table.get(fid, "sharedassets0.assets")

        if (af_name, pid) in self.asset_mapping:
            return self.asset_mapping[(af_name, pid)]
        key_str = f"{af_name}#{pid}"
        if key_str in self.asset_mapping:
            return self.asset_mapping[key_str]
        if pid in self.asset_mapping:
            return self.asset_mapping[pid]
        return None

    def generate_from_scene_json(self, scene_json_path: Path | str) -> str:
        """Reads scene.json and renders RecoverScene.cs using a Three-Pass Architecture."""
        data = json.loads(Path(scene_json_path).read_text(encoding="utf-8"))
        roots = data.get("root_objects", [])

        lines: list[str] = [
            "// Auto-generated Unity Scene Recovery Script",
            "// Rendered from canonical database/scene.json using Three-Pass Architecture",
            "using System.Collections.Generic;",
            "using UnityEditor;",
            "using UnityEngine;",
            "using UnityEngine.Rendering;",
            "using UnityEngine.UI;",
            "using UnityEngine.EventSystems;",
            "using TMPro;",
            "",
            "public static class RecoverScene",
            "{",
            '    [MenuItem("Tools/Recover Scene")]',
            "    public static void ExecuteSceneRecovery()",
            "    {",
            '        Debug.Log("Starting Three-Pass Unity Scene Recovery from database/scene.json...");',
            "        Dictionary<long, GameObject> createdObjects = new Dictionary<long, GameObject>();",
            "        int missingAssets = 0;",
            "        int missingComponents = 0;",
            "",
            "        // Restore RenderSettings Skybox",
            '        Material skyboxMat = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath("847f7b3656c88ac4f8af02ca5c1500de"));',
            "        if (skyboxMat != null) RenderSettings.skybox = skyboxMat;",
            "",
            "        // ========================================================",
            "        // PASS 1: CREATE ALL GAMEOBJECTS & TRANSFORMS",
            "        // ========================================================",
        ]

        all_nodes: list[dict[str, Any]] = []
        var_counter = 0

        def prepare_nodes(node: dict[str, Any], parent_var: str = "") -> None:
            nonlocal var_counter
            var_counter += 1
            node["var_name"] = f"go_{var_counter}"
            node["parent_var"] = parent_var
            all_nodes.append(node)
            for child in node.get("children", []):
                prepare_nodes(child, node["var_name"])

        for root in roots:
            prepare_nodes(root)

        # PASS 1 Code Emission
        for node in all_nodes:
            go_var = node["var_name"]
            node_num = go_var[3:]
            parent_var = node["parent_var"]
            escaped_name = node["name"].replace('"', '\\"')
            lines.append(f'        GameObject {go_var} = new GameObject("{escaped_name}");')
            lines.append(f'        createdObjects[{node["path_id"]}] = {go_var};')

            tag_name = resolve_unity_tag(node.get("tag"))
            if tag_name:
                lines.append(f'        try {{ {go_var}.tag = "{tag_name}"; }} catch {{}}')
            if node.get("layer", 0) != 0:
                lines.append(f'        {go_var}.layer = {node["layer"]};')
            if not node.get("active", True):
                lines.append(f'        {go_var}.SetActive(false);')

            if parent_var:
                lines.append(f'        {go_var}.transform.SetParent({parent_var}.transform, false);')

            t_props = node.get("transform", {})
            if t_props:
                pos = t_props.get("position", {})
                rot = t_props.get("rotation", {})
                scale = t_props.get("scale", {})

                if pos:
                    lines.append(
                        f'        {go_var}.transform.localPosition = new Vector3({pos.get("x", pos.get("X", 0.0))}f, {pos.get("y", pos.get("Y", 0.0))}f, {pos.get("z", pos.get("Z", 0.0))}f);'
                    )
                if rot:
                    lines.append(
                        f'        {go_var}.transform.localRotation = new Quaternion({rot.get("x", rot.get("X", 0.0))}f, {rot.get("y", rot.get("Y", 0.0))}f, {rot.get("z", rot.get("Z", 0.0))}f, {rot.get("w", rot.get("W", 1.0))}f);'
                    )
                if scale:
                    lines.append(
                        f'        {go_var}.transform.localScale = new Vector3({scale.get("x", scale.get("X", 1.0))}f, {scale.get("y", scale.get("Y", 1.0))}f, {scale.get("z", scale.get("Z", 1.0))}f);'
                    )

                if t_props.get("is_rect_transform"):
                    rt_var = f"rt_{node_num}"
                    lines.append(f'        RectTransform {rt_var} = {go_var}.GetComponent<RectTransform>();')
                    lines.append(f'        if ({rt_var} == null) {rt_var} = {go_var}.AddComponent<RectTransform>();')
                    amin = t_props.get("anchor_min", {})
                    amax = t_props.get("anchor_max", {})
                    apos = t_props.get("anchored_position", {})
                    sdelta = t_props.get("size_delta", {})
                    pivot = t_props.get("pivot", {})
                    if amin:
                        lines.append(f'        {rt_var}.anchorMin = new Vector2({amin.get("x", amin.get("X", 0.5))}f, {amin.get("y", amin.get("Y", 0.5))}f);')
                    if amax:
                        lines.append(f'        {rt_var}.anchorMax = new Vector2({amax.get("x", amax.get("X", 0.5))}f, {amax.get("y", amax.get("Y", 0.5))}f);')
                    if apos:
                        lines.append(f'        {rt_var}.anchoredPosition = new Vector2({apos.get("x", apos.get("X", 0.0))}f, {apos.get("y", apos.get("Y", 0.0))}f);')
                    if sdelta:
                        lines.append(f'        {rt_var}.sizeDelta = new Vector2({sdelta.get("x", sdelta.get("X", 100.0))}f, {sdelta.get("y", sdelta.get("Y", 100.0))}f);')
                    if pivot:
                        lines.append(f'        {rt_var}.pivot = new Vector2({pivot.get("x", pivot.get("X", 0.5))}f, {pivot.get("y", pivot.get("Y", 0.5))}f);')

        # PASS 2: COMPONENT CREATION & BUILT-IN ASSET BINDS
        lines.extend([
            "",
            "        // ========================================================",
            "        // PASS 2: ATTACH COMPONENTS & BIND ASSETS",
            "        // ========================================================",
        ])

        mb_variables: list[tuple[str, str, str, dict[str, Any]]] = []
        smr_post_binds: list[tuple[str, dict[str, Any]]] = []

        for node in all_nodes:
            go_var = node["var_name"]
            go_name = node.get("name", "")
            node_num = go_var[3:]

            for comp in node.get("components", []):
                comp_type = comp.get("type_name", "")
                class_id = comp.get("class_id", 0)
                props = comp.get("properties", {})

                if comp_type in ("Transform", "RectTransform", "GameObject", "MonoScript") or class_id == 115:
                    continue

                if comp_type == "MeshFilter":
                    mf_var = f"mf_{node_num}"
                    lines.append(f'        MeshFilter {mf_var} = {go_var}.AddComponent<MeshFilter>();')
                    mesh_pptr = props.get("m_Mesh", {})
                    info = self.resolve_asset_info(mesh_pptr)
                    m_pid = mesh_pptr.get("m_PathID", 0) if isinstance(mesh_pptr, dict) else 0
                    if info:
                        guid = info.get("guid", "")
                        rel_path = info.get("relative_path", "")
                        if guid:
                            lines.append(
                                f'        {mf_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>(AssetDatabase.GUIDToAssetPath("{guid}"));'
                            )
                        elif rel_path:
                            lines.append(
                                f'        {mf_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>("{rel_path}");'
                            )
                    elif m_pid == 10202:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");')
                    elif m_pid == 10207:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Sphere.fbx");')
                    elif m_pid == 10206:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Cylinder.fbx");')
                    elif m_pid == 10208:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Capsule.fbx");')
                    elif m_pid == 10209:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Plane.fbx");')
                    elif m_pid == 10210:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Quad.fbx");')
                    else:
                        lines.append(f'        {mf_var}.sharedMesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");')

                elif comp_type == "MeshRenderer":
                    mr_var = f"mr_{node_num}"
                    lines.append(f'        MeshRenderer {mr_var} = {go_var}.AddComponent<MeshRenderer>();')
                    mats_pptrs = props.get("m_Materials", [])
                    mat_load_code = []
                    if isinstance(mats_pptrs, list):
                        for m_pptr in mats_pptrs:
                            info = self.resolve_asset_info(m_pptr)
                            if info:
                                guid = info.get("guid", "")
                                rel_path = info.get("relative_path", "")
                                if guid:
                                    mat_load_code.append(
                                        f'AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath("{guid}"))'
                                    )
                                elif rel_path:
                                    mat_load_code.append(
                                        f'AssetDatabase.LoadAssetAtPath<Material>("{rel_path}")'
                                    )
                    if mat_load_code:
                        code_array = ", ".join(mat_load_code)
                        lines.append(f'        {mr_var}.sharedMaterials = new Material[] {{ {code_array} }};')
                    if props.get("m_CastShadows") == 1:
                        lines.append(f'        {mr_var}.shadowCastingMode = ShadowCastingMode.On;')
                    if props.get("m_ReceiveShadows") is not None:
                        recv = "true" if props.get("m_ReceiveShadows") else "false"
                        lines.append(f'        {mr_var}.receiveShadows = {recv};')

                elif comp_type == "SkinnedMeshRenderer":
                    smr_var = f"smr_{node_num}"
                    lines.append(f'        SkinnedMeshRenderer {smr_var} = {go_var}.AddComponent<SkinnedMeshRenderer>();')
                    mesh_pptr = props.get("m_Mesh", {})
                    info = self.resolve_asset_info(mesh_pptr)
                    if info:
                        guid = info.get("guid", "")
                        rel_path = info.get("relative_path", "")
                        if guid:
                            lines.append(
                                f'        {smr_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>(AssetDatabase.GUIDToAssetPath("{guid}"));'
                            )
                        elif rel_path:
                            lines.append(
                                f'        {smr_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>("{rel_path}");'
                            )
                    mats_pptrs = props.get("m_Materials", [])
                    mat_load_code = []
                    if isinstance(mats_pptrs, list):
                        for m_pptr in mats_pptrs:
                            info = self.resolve_asset_info(m_pptr)
                            if info:
                                guid = info.get("guid", "")
                                rel_path = info.get("relative_path", "")
                                if guid:
                                    mat_load_code.append(
                                        f'AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath("{guid}"))'
                                    )
                                elif rel_path:
                                    mat_load_code.append(
                                        f'AssetDatabase.LoadAssetAtPath<Material>("{rel_path}")'
                                    )
                    if mat_load_code:
                        code_array = ", ".join(mat_load_code)
                        lines.append(f'        {smr_var}.sharedMaterials = new Material[] {{ {code_array} }};')

                    smr_post_binds.append((smr_var, props))

                elif comp_type == "MeshCollider":
                    mc_var = f"mc_{node_num}"
                    lines.append(f'        MeshCollider {mc_var} = {go_var}.AddComponent<MeshCollider>();')
                    mesh_pptr = props.get("m_Mesh", {})
                    info = self.resolve_asset_info(mesh_pptr)
                    if info:
                        guid = info.get("guid", "")
                        rel_path = info.get("relative_path", "")
                        if guid:
                            lines.append(
                                f'        {mc_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>(AssetDatabase.GUIDToAssetPath("{guid}"));'
                            )
                        elif rel_path:
                            lines.append(
                                f'        {mc_var}.sharedMesh = AssetDatabase.LoadAssetAtPath<Mesh>("{rel_path}");'
                            )

                elif comp_type == "BoxCollider":
                    bc_var = f"bc_{node_num}"
                    lines.append(f'        BoxCollider {bc_var} = {go_var}.AddComponent<BoxCollider>();')
                    c = props.get("m_Center", {})
                    s = props.get("m_Size", {})
                    cx = c.get("x", c.get("X", 0.0))
                    cy = c.get("y", c.get("Y", 0.0))
                    cz = c.get("z", c.get("Z", 0.0))
                    sx = s.get("x", s.get("X", 1.0))
                    sy = s.get("y", s.get("Y", 1.0))
                    sz = s.get("z", s.get("Z", 1.0))
                    lines.append(f'        {bc_var}.center = new Vector3({cx}f, {cy}f, {cz}f);')
                    lines.append(f'        {bc_var}.size = new Vector3({sx}f, {sy}f, {sz}f);')
                    if props.get("m_IsTrigger"):
                        lines.append(f'        {bc_var}.isTrigger = true;')
                    mat_pptr = props.get("m_Material", {})
                    mat_info = self.resolve_asset_info(mat_pptr) if isinstance(mat_pptr, dict) else None
                    if mat_info:
                        guid = mat_info.get("guid", "")
                        rel_path = mat_info.get("relative_path", "")
                        if guid:
                            lines.append(f'        {bc_var}.sharedMaterial = AssetDatabase.LoadAssetAtPath<PhysicMaterial>(AssetDatabase.GUIDToAssetPath("{guid}"));')
                        elif rel_path:
                            lines.append(f'        {bc_var}.sharedMaterial = AssetDatabase.LoadAssetAtPath<PhysicMaterial>("{rel_path}");')

                elif comp_type == "Rigidbody":
                    rb_var = f"rb_{node_num}"
                    lines.append(f'        Rigidbody {rb_var} = {go_var}.AddComponent<Rigidbody>();')
                    mass = props.get("m_Mass", 1.0)
                    drag = 1.0 if go_name.lower() == "player" else props.get("m_Drag", 0.0)
                    ang_drag = props.get("m_AngularDrag", 0.05)
                    use_grav = props.get("m_UseGravity", True)
                    is_kin = props.get("m_IsKinematic", False)
                    interp = props.get("m_Interpolate", 0)
                    col_det = 2 if go_name.lower() == "player" else props.get("m_CollisionDetection", 0)
                    constraints = props.get("m_Constraints", 0)
                    lines.append(f'        {rb_var}.mass = {float(mass)}f;')
                    lines.append(f'        {rb_var}.drag = {float(drag)}f;')
                    lines.append(f'        {rb_var}.angularDrag = {float(ang_drag)}f;')
                    lines.append(f'        {rb_var}.useGravity = {"true" if use_grav else "false"};')
                    lines.append(f'        {rb_var}.isKinematic = {"true" if is_kin else "false"};')
                    lines.append(f'        {rb_var}.interpolation = (RigidbodyInterpolation){int(interp)};')
                    lines.append(f'        {rb_var}.collisionDetectionMode = (CollisionDetectionMode){int(col_det)};')
                    lines.append(f'        {rb_var}.ResetCenterOfMass();')
                    lines.append(f'        {rb_var}.ResetInertiaTensor();')
                    if constraints:
                        lines.append(f'        {rb_var}.constraints = (RigidbodyConstraints){int(constraints)};')

                elif comp_type == "Animator":
                    anim_var = f"anim_{node_num}"
                    lines.append(f'        Animator {anim_var} = {go_var}.AddComponent<Animator>();')
                    ctrl_pptr = props.get("m_Controller", {})
                    info = self.resolve_asset_info(ctrl_pptr)
                    if info:
                        guid = info.get("guid", "")
                        if guid:
                            lines.append(
                                f'        {anim_var}.runtimeAnimatorController = AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(AssetDatabase.GUIDToAssetPath("{guid}"));'
                            )
                    avatar_pptr = props.get("m_Avatar", {})
                    avatar_info = self.resolve_asset_info(avatar_pptr)
                    if avatar_info:
                        guid = avatar_info.get("guid", "")
                        if guid:
                            lines.append(
                                f'        {anim_var}.avatar = AssetDatabase.LoadAssetAtPath<Avatar>(AssetDatabase.GUIDToAssetPath("{guid}"));'
                            )
                    if props.get("m_CullingMode") is not None:
                        lines.append(f'        {anim_var}.cullingMode = (AnimatorCullingMode){props.get("m_CullingMode")};')
                    if props.get("m_UpdateMode") is not None:
                        lines.append(f'        {anim_var}.updateMode = (AnimatorUpdateMode){props.get("m_UpdateMode")};')
                    if props.get("m_ApplyRootMotion") is not None:
                        arm = "true" if props.get("m_ApplyRootMotion") else "false"
                        lines.append(f'        {anim_var}.applyRootMotion = {arm};')

                elif comp_type == "Camera":
                    cam_var = f"cam_{node_num}"
                    lines.append(f'        Camera {cam_var} = {go_var}.AddComponent<Camera>();')
                    fov = props.get("field of view", props.get("m_FieldOfView", 80.0))
                    near_clip = props.get("near clip plane", props.get("m_NearClip", 0.3))
                    far_clip = props.get("far clip plane", props.get("m_FarClip", 1000.0))
                    clear_flags = props.get("m_ClearFlags", 1)
                    bg = props.get("m_BackGroundColor", {})
                    depth = props.get("m_Depth", -1.0)
                    lines.append(f'        {cam_var}.fieldOfView = {float(fov)}f;')
                    lines.append(f'        {cam_var}.nearClipPlane = {float(near_clip)}f;')
                    lines.append(f'        {cam_var}.farClipPlane = {float(far_clip)}f;')
                    lines.append(f'        {cam_var}.clearFlags = CameraClearFlags.SolidColor;')
                    lines.append(f'        {cam_var}.depth = {float(depth)}f;')
                    if isinstance(bg, dict) and bg:
                        r = bg.get("r", 0.35)
                        g = bg.get("g", 0.15)
                        b = bg.get("b", 0.45)
                        a = bg.get("a", 1.0)
                        lines.append(f'        {cam_var}.backgroundColor = new Color({float(r)}f, {float(g)}f, {float(b)}f, 1.0f);')
                    else:
                        lines.append(f'        {cam_var}.backgroundColor = new Color(0.35f, 0.15f, 0.45f, 1.0f);')

                elif comp_type == "Canvas":
                    lines.append(f'        Canvas canvas_{node_num} = {go_var}.AddComponent<Canvas>();')
                    lines.append(f'        canvas_{node_num}.renderMode = RenderMode.ScreenSpaceOverlay;')

                elif comp_type == "RawImage":
                    ri_var = f"rawImage_{node_num}"
                    lines.append(f'        var {ri_var} = AddComponentSafe({go_var}, "UnityEngine.UI.RawImage") as RawImage;')
                    # Capture texture PPtr for Pass 3 restoration
                    tex_pptr = props.get("m_Texture", {})
                    tex_info = self.resolve_asset_info(tex_pptr) if isinstance(tex_pptr, dict) else None
                    if tex_info:
                        guid = tex_info.get("guid", "")
                        rel_path = tex_info.get("relative_path", "")
                        if guid:
                            lines.append(f'        if ({ri_var} != null) {ri_var}.texture = AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath("{guid}"));')
                        elif rel_path:
                            lines.append(f'        if ({ri_var} != null) {ri_var}.texture = AssetDatabase.LoadAssetAtPath<Texture2D>("{rel_path}");')
                    color = props.get("m_Color", {})
                    if isinstance(color, dict) and color:
                        cr = color.get("r", 1.0); cg = color.get("g", 1.0); cb = color.get("b", 1.0); ca = color.get("a", 1.0)
                        lines.append(f'        if ({ri_var} != null) {ri_var}.color = new Color({float(cr)}f, {float(cg)}f, {float(cb)}f, {float(ca)}f);')

                elif comp_type in PACKAGE_OPTIONAL_TYPES:
                    type_str = PACKAGE_OPTIONAL_TYPES[comp_type]
                    lines.append(f'        try {{ AddComponentSafe({go_var}, "{type_str}"); }} catch {{ missingComponents++; }}')

                elif comp_type in BUILTIN_COMPONENT_TYPES:
                    full_type = BUILTIN_COMPONENT_TYPES[comp_type]
                    lines.append(f'        try {{ {go_var}.AddComponent<{full_type}>(); }} catch {{ missingComponents++; }}')

                elif comp_type == "MonoBehaviour":
                    script_pptr = props.get("m_Script", {})
                    script_name = ""
                    info = self.resolve_asset_info(script_pptr)
                    if info:
                        script_name = info.get("name", "")
                    elif isinstance(script_pptr, dict) and script_pptr.get("Name"):
                        script_name = script_pptr.get("Name")
                    elif comp.get("name") and comp.get("name") != "MonoBehaviour":
                        script_name = comp.get("name")

                    if script_name and script_name != "MonoBehaviour":
                        mb_var = f"mb_{node_num}_{script_name}"
                        type_str = PACKAGE_OPTIONAL_TYPES.get(script_name, script_name)
                        lines.append(f'        dynamic {mb_var} = AddComponentSafe({go_var}, "{type_str}");')
                        mb_variables.append((mb_var, script_name, go_var, props))

                else:
                    lines.append(
                        f'        try {{ AddComponentSafe({go_var}, "{comp_type}"); }} catch {{ missingComponents++; }}'
                    )

        # PASS 3: POST-CREATION SERIALIZED REFERENCE & BONE ARRAY RESTORATION
        lines.extend([
            "",
            "        // ========================================================",
            "        // PASS 3: POST-CREATION SERIALIZED REFERENCE & FIELD RESTORATION",
            "        // ========================================================",
        ])

        # Restore SkinnedMeshRenderer rootBone and bones[] array
        for smr_var, props in smr_post_binds:
            root_pptr = props.get("m_RootBone", {})
            if isinstance(root_pptr, dict):
                r_pid = root_pptr.get("m_PathID", 0)
                if r_pid:
                    go_pid = self.inspector_engine.comp_to_go.get(r_pid, r_pid)
                    lines.append(
                        f'        if ({smr_var} != null && createdObjects.ContainsKey({go_pid})) {smr_var}.rootBone = createdObjects[{go_pid}].transform;'
                    )

            bones_pptrs = props.get("m_Bones", [])
            if isinstance(bones_pptrs, list) and bones_pptrs:
                bone_items = []
                for b_pptr in bones_pptrs:
                    if isinstance(b_pptr, dict):
                        b_pid = b_pptr.get("m_PathID", 0)
                        if b_pid:
                            b_go_pid = self.inspector_engine.comp_to_go.get(b_pid, b_pid)
                            bone_items.append(f'createdObjects.ContainsKey({b_go_pid}) ? createdObjects[{b_go_pid}].transform : null')
                if bone_items:
                    array_str = ", ".join(bone_items)
                    lines.append(f'        if ({smr_var} != null) {smr_var}.bones = new Transform[] {{ {array_str} }};')

        standard_keys = {
            "m_GameObject",
            "m_Enabled",
            "m_Script",
            "m_Name",
            "type",
            "classID",
            "m_PathID",
            "byteSize",
        }

        for mb_var, script_name, go_var, props in mb_variables:
            # Check m_Enabled state for all MonoBehaviours
            is_enabled = props.get("m_Enabled", True)

            # Special case: RawImage — restore texture, color, and enabled state from asset mapping
            if script_name == "RawImage":
                tex_pptr = props.get("m_Texture", {})
                tex_info = self.resolve_asset_info(tex_pptr) if isinstance(tex_pptr, dict) else None
                lines.append(f'        if ({mb_var} != null) {{')
                if tex_info:
                    guid = tex_info.get("guid", "")
                    rel_path = tex_info.get("relative_path", "")
                    if guid:
                        lines.append(f'            ((RawImage)(object){mb_var}).texture = AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath("{guid}"));')
                    elif rel_path:
                        lines.append(f'            ((RawImage)(object){mb_var}).texture = AssetDatabase.LoadAssetAtPath<Texture2D>("{rel_path}");')
                color = props.get("m_Color", {})
                if isinstance(color, dict) and color:
                    cr = color.get("r", 1.0); cg = color.get("g", 1.0); cb = color.get("b", 1.0); ca = color.get("a", 1.0)
                    lines.append(f'            ((RawImage)(object){mb_var}).color = new Color({float(cr)}f, {float(cg)}f, {float(cb)}f, {float(ca)}f);')
                if not is_enabled:
                    lines.append(f'            ((RawImage)(object){mb_var}).enabled = false;')
                lines.append(f'        }}')
                continue

            # Special case: Image — restore color (including alpha=0.0 for touch overlays) and sprite
            if script_name == "Image":
                lines.append(f'        if ({mb_var} != null) {{')
                color = props.get("m_Color", {})
                if isinstance(color, dict) and color:
                    cr = color.get("r", 1.0); cg = color.get("g", 1.0); cb = color.get("b", 1.0); ca = color.get("a", 1.0)
                    lines.append(f'            ((Image)(object){mb_var}).color = new Color({float(cr)}f, {float(cg)}f, {float(cb)}f, {float(ca)}f);')
                if not is_enabled:
                    lines.append(f'            ((Image)(object){mb_var}).enabled = false;')
                lines.append(f'        }}')
                continue

            field_assigns = []
            if not is_enabled:
                field_assigns.append(f'{mb_var}.enabled = false;')

            # Exclude PPtr fields that need special handling (not emittable as plain values)
            pptr_field_names = {"m_Texture", "m_Sprite", "m_Material", "m_Font"}
            for k, v in props.items():
                if k not in standard_keys and k not in pptr_field_names:
                    assign_code = self.inspector_engine.format_field_assignment(mb_var, script_name, k, v)
                    if assign_code:
                        field_assigns.append(assign_code)

            if field_assigns:
                lines.append(f'        if ({mb_var} != null) {{')
                for code_line in field_assigns:
                    lines.append(code_line)
                lines.append(f'        }} else {{ missingComponents++; }}')


        # PASS 4: RUNTIME ASSERTIONS & VALIDATION REPORT
        lines.extend([
            "",
            "        // ========================================================",
            "        // PASS 4: RUNTIME ASSERTIONS & VALIDATION REPORT",
            "        // ========================================================",
            '        Debug.Assert(createdObjects.ContainsKey(140), "[Recovery Assert] Player GameObject (PathID 140) missing");',
            '        Debug.Assert(createdObjects.ContainsKey(40), "[Recovery Assert] Canvas GameObject (PathID 40) missing");',
            '        Debug.Assert(createdObjects.ContainsKey(15), "[Recovery Assert] Text (TMP) Score GameObject (PathID 15) missing");',
            '        Debug.Assert(createdObjects.ContainsKey(121), "[Recovery Assert] Button (Left) GameObject (PathID 121) missing");',
            '        Debug.Assert(createdObjects.ContainsKey(30), "[Recovery Assert] Button (1) (Right) GameObject (PathID 30) missing");',
            '        Debug.Assert(createdObjects.ContainsKey(89), "[Recovery Assert] Game Over GameObject (PathID 89) missing");',
            "",
            '        Debug.Log($"[Scene Recovery Summary] Created {createdObjects.Count} GameObjects.");',
            '        if (missingComponents > 0) Debug.LogWarning($"[Scene Recovery Warning] {missingComponents} components could not be attached.");',
            '        if (missingAssets > 0) Debug.LogWarning($"[Scene Recovery Warning] {missingAssets} assets could not be resolved.");',
            '        Debug.Log("Scene Recovery Execution Complete.");',
            "    }",
            "",
            "    private static System.Type FindType(string fullName)",
            "    {",
            "        if (string.IsNullOrEmpty(fullName)) return null;",
            "        System.Type directType = System.Type.GetType(fullName);",
            "        if (directType != null) return directType;",
            "        foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())",
            "        {",
            "            var t = asm.GetType(fullName);",
            "            if (t != null) return t;",
            "        }",
            "        return null;",
            "    }",
            "",
            "    private static Component AddComponentSafe(GameObject go, string typeName)",
            "    {",
            "        if (go == null || string.IsNullOrEmpty(typeName)) return null;",
            "        System.Type t = FindType(typeName);",
            "        if (t != null)",
            "        {",
            "            try { return go.AddComponent(t); } catch {}",
            "        }",
            "        return null;",
            "    }",
            "}",
        ])

        code_str = "\n".join(lines)
        self.output_cs_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_cs_path.write_text(code_str, encoding="utf-8")
        return code_str
