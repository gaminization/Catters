# Master Deep Inventory & Reverse-Engineering Diagnostic Report

Exhaustive object inventory, term search, script trace, mesh resolution, and tool comparison audit.

## Phase 1 — Inventory EVERYTHING

**Total Parsed Unity Objects:** 2836

| Object Type | Count | Description / Role |
|---|---|---|
| `MonoScript` | **1071** | Serialized Unity Object Type |
| `GameObject` | **329** | Serialized Unity Object Type |
| `Transform` | **324** | Serialized Unity Object Type |
| `MeshRenderer` | **263** | Serialized Unity Object Type |
| `MeshFilter` | **263** | Serialized Unity Object Type |
| `BoxCollider` | **261** | Serialized Unity Object Type |
| `Animator` | **113** | Serialized Unity Object Type |
| `Shader` | **52** | Serialized Unity Object Type |
| `Material` | **38** | Serialized Unity Object Type |
| `MonoBehaviour` | **32** | Serialized Unity Object Type |
| `Texture2D` | **27** | Serialized Unity Object Type |
| `Font` | **6** | Serialized Unity Object Type |
| `RectTransform` | **5** | Serialized Unity Object Type |
| `Mesh` | **4** | Serialized Unity Object Type |
| `CanvasRenderer` | **4** | Serialized Unity Object Type |
| `MeshCollider` | **3** | Serialized Unity Object Type |
| `PreloadData` | **2** | Serialized Unity Object Type |
| `Sprite` | **2** | Serialized Unity Object Type |
| `Avatar` | **2** | Serialized Unity Object Type |
| `TextAsset` | **2** | Serialized Unity Object Type |
| `PlayerSettings` | **1** | Serialized Unity Object Type |
| `InputManager` | **1** | Serialized Unity Object Type |
| `TagManager` | **1** | Serialized Unity Object Type |
| `AudioManager` | **1** | Serialized Unity Object Type |
| `ScriptMapper` | **1** | Serialized Unity Object Type |
| `MonoManager` | **1** | Serialized Unity Object Type |
| `GraphicsSettings` | **1** | Serialized Unity Object Type |
| `TimeManager` | **1** | Serialized Unity Object Type |
| `DelayedCallManager` | **1** | Serialized Unity Object Type |
| `PhysicsManager` | **1** | Serialized Unity Object Type |
| `BuildSettings` | **1** | Serialized Unity Object Type |
| `QualitySettings` | **1** | Serialized Unity Object Type |
| `ResourceManager` | **1** | Serialized Unity Object Type |
| `NavMeshProjectSettings` | **1** | Serialized Unity Object Type |
| `Physics2DSettings` | **1** | Serialized Unity Object Type |
| `RuntimeInitializeOnLoadManager` | **1** | Serialized Unity Object Type |
| `StreamingManager` | **1** | Serialized Unity Object Type |
| `VFXManager` | **1** | Serialized Unity Object Type |
| `AnimationClip` | **1** | Serialized Unity Object Type |
| `Cubemap` | **1** | Serialized Unity Object Type |
| `AnimatorController` | **1** | Serialized Unity Object Type |
| `PhysicMaterial` | **1** | Serialized Unity Object Type |
| `LightProbes` | **1** | Serialized Unity Object Type |
| `Camera` | **1** | Serialized Unity Object Type |
| `Rigidbody` | **1** | Serialized Unity Object Type |
| `AudioListener` | **1** | Serialized Unity Object Type |
| `RenderSettings` | **1** | Serialized Unity Object Type |
| `Light` | **1** | Serialized Unity Object Type |
| `SkinnedMeshRenderer` | **1** | Serialized Unity Object Type |
| `LightmapSettings` | **1** | Serialized Unity Object Type |
| `NavMeshSettings` | **1** | Serialized Unity Object Type |
| `Canvas` | **1** | Serialized Unity Object Type |
| `LightingSettings` | **1** | Serialized Unity Object Type |

## Phase 2 — Find Every Player-like Object Search Results

Searched across all 1,575 serialized objects for terms: `player, cat, runner, camera, gamemanager, score, obstacle, coin, ground, spawner`.
Found **366** matching objects.

| PathID | Type Name | Name / Property | Matched Search Terms |
|---|---|---|---|
| `1` | `PlayerSettings` | `PlayerSettings_#1` | `player, cat, ground` |
| `3` | `TagManager` | `TagManager_#3` | `obstacle` |
| `5` | `ScriptMapper` | `ScriptMapper_#5` | `camera` |
| `7` | `GraphicsSettings` | `GraphicsSettings_#7` | `camera` |
| `11` | `BuildSettings` | `BuildSettings_#11` | `cat` |
| `12` | `QualitySettings` | `QualitySettings_#12` | `camera` |
| `6` | `Shader` | `` | `player` |
| `7` | `Shader` | `` | `player` |
| `19` | `Shader` | `` | `player` |
| `62` | `Shader` | `` | `player` |
| `64` | `Shader` | `` | `player` |
| `65` | `Shader` | `` | `player` |
| `66` | `Shader` | `` | `player, cat` |
| `67` | `Shader` | `` | `player` |
| `68` | `Shader` | `` | `player` |
| `69` | `Shader` | `` | `player, ground` |
| `74` | `Shader` | `` | `player` |
| `75` | `Shader` | `` | `player` |
| `102` | `Shader` | `` | `player` |
| `105` | `Shader` | `` | `player` |
| `107` | `Shader` | `` | `player, cat` |
| `109` | `Shader` | `` | `player, cat` |
| `110` | `Shader` | `` | `player` |
| `111` | `Shader` | `` | `player` |
| `113` | `Shader` | `` | `player` |
| `9000` | `Shader` | `` | `player` |
| `9001` | `Shader` | `` | `player` |
| `9002` | `Shader` | `` | `player` |
| `9003` | `Shader` | `` | `player` |
| `9004` | `Shader` | `` | `player` |
| `9007` | `Shader` | `` | `player` |
| `9100` | `Shader` | `` | `player` |
| `9101` | `Shader` | `` | `player` |
| `9102` | `Shader` | `` | `player` |
| `10753` | `Shader` | `` | `player` |
| `10757` | `Shader` | `` | `player` |
| `10770` | `Shader` | `` | `player` |
| `15104` | `Shader` | `` | `player` |
| `15105` | `Shader` | `` | `player` |
| `15106` | `Shader` | `` | `player, ground` |
| ... | ... | *(Total 366 matched objects)* | ... |

## Phase 3 — Trace Every MonoBehaviour C# Class

Total C# Scripts in `Assembly-CSharp`: **8**
Total MonoBehaviour instances in dump: **32**

| Script Class Name | Referencing MonoBehaviour PathID | Attached GameObject Name (PathID) | Recovered Status |
|---|---|---|---|
| `AssemblyInfo` | None | None | **Class exists in Assembly-CSharp, but not instantiated in level scene dump** |
| `FollowPlayer` | YES | `MonoBehaviour 1584 -> Main Camera (56)` | **RECOVERED** |
| `GameEnd` | YES | `MonoBehaviour 1589 -> player (140)` | **RECOVERED** |
| `GameManager` | YES | `MonoBehaviour 1586 -> GameManager (98)` | **RECOVERED** |
| `MyButton` | YES | `MonoBehaviour 1581 -> Button (1) (30)` | **RECOVERED** |
| `MyButton` | YES | `MonoBehaviour 1591 -> Button (121)` | **RECOVERED** |
| `PlayerCollision` | YES | `MonoBehaviour 1588 -> player (140)` | **RECOVERED** |
| `PlayerMovement` | YES | `MonoBehaviour 1587 -> player (140)` | **RECOVERED** |
| `Score` | YES | `MonoBehaviour 1579 -> Text (TMP) (15)` | **RECOVERED** |

## Phase 4 — Trace Unresolved Meshes

Total Unresolved Meshes: **266**

| GameObject Name | Component Type | Mesh PathID | Exists in Registry | Exported in AssetRipper | GUID | Cause / Reason |
|---|---|---|---|---|---|---|
| `fence_double (44)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (8)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (19)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `Cube` | `MeshFilter` | `10202` | `NO` | `NO` | `—` | Missing Mesh object |
| `fence_double (7)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (2)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (32)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (31)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (36)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (50)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (23)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (49)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (36)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (3)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (1)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (4)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (47)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (10)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (30)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (37)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (38)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (28)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (53)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (13)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (46)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (47)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (35)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (40)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (16)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (53)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `Cloud_Cumulus_Fluffy (2)` | `MeshFilter` | `18` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (3)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (1)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (18)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (6)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (54)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (50)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (15)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `Cloud_Cumulus_Fluffy` | `MeshFilter` | `18` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (14)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (22)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (11)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (54)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (45)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (25)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (20)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `Cloud_Cumulus_Fluffy (1)` | `MeshFilter` | `18` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (20)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (28)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |
| `fence_double (34)` | `MeshFilter` | `17` | `YES` | `NO` | `—` | Mesh embedded inside FBX model asset or non-exported asset |

## Phase 5 — AssetStudio vs AssetRipper Comparison & APK Data File Audit

### Comparison Breakdown
- **AssetStudio Dump (`assetdump/`):** Contains raw JSON object dumps extracted from single scene bundle (`1,575` UnityObjects across `137` GameObjects). Contains level environment geometry (`Obstacles`, `Clouds`, `Fences`, `Canvas`, `Directional Light`).
- **AssetRipper Export (`ExportProject/`):** Exported `61` Materials, `94` Meshes, `184` Texture2Ds, and all C# scripts (`PlayerMovement.cs`, `GameManager.cs`, etc.).

### APK Binary Data File Audit (`assets/bin/Data/`)
- Checking workspace for APK binary files (`globalgamemanagers`, `sharedassets0.assets`, `level0`, `resources.assets`):
- **Findings:** The current project directory `cattersrecovery` contains pre-extracted dumps in `cattersrecovered/`. Raw APK binary files (`.assets`, `globalgamemanagers`) were processed upstream during initial AssetStudio / AssetRipper dump extraction.
- **Conclusion:** Objects such as `PlayerMovement.cs` and `GameManager.cs` exist in Assembly-CSharp, proving that Player/GameManager code is compiled in the game binary. However, the specific serialized asset dump provided in `cattersrecovered/assetstudio/assetdump/` corresponds to the level environment asset dump, which does not contain the Player prefab or GameManager instance in this scene.