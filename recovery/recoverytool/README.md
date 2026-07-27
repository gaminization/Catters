# Unity Scene Recovery & Reconstruction Audit Framework (`recoverytool`)

An automated, modular, and deterministic Unity scene recovery and reconstruction audit framework built in Python 3.12. It reconstructs original Unity scenes by parsing raw AssetStudio object dumps (`cattersrecovered/assetstudio/assetdump/`), building a MultiDiGraph scene graph using NetworkX, resolving asset GUIDs against AssetRipper's `ExportedProject`, generating a canonical database (`database/scene.json`), and rendering a C# Unity Editor recovery script (`RecoverScene.cs`) with console self-validation.

---

## Workspace Structure

```
cattersrecovery/
├── cattersrecovered/
│   ├── assetripper/ExportedProject/    # Source Assets, Scripts, and .meta files
│   └── assetstudio/assetdump/          # Raw dumped JSON objects
├── recoverytool/
│   ├── parser/                          # UnityObject parsers & dump reader
│   ├── resolver/                        # PathID registry, PPtr resolver, asset matcher
│   ├── graph/                           # NetworkX MultiDiGraph SceneGraph builder & traversal
│   ├── generator/                       # Hierarchy reconstructor & C# code generator
│   ├── editor/                          # Inspector field recovery & validator
│   ├── auditors/                        # Phase C-F Transform, Component, Asset, MonoBehaviour auditors
│   ├── database/                        # Phase A & I Stable Canonical JSON Database Files
│   │   ├── scene.json                   # Canonical single source of truth for recovered scene
│   │   ├── objects.json
│   │   ├── references.json
│   │   ├── graph.json
│   │   ├── assets.json
│   │   └── validation.json
│   ├── visualizers/                     # Phase G & H Interactive HTML Graph visualizers
│   ├── generated/                       # Output RecoverScene.cs C# script
│   ├── reports/                         # Phase B-J & N Markdown reports & interactive HTML
│   │   ├── scene_diff.md
│   │   ├── transform_validation.md
│   │   ├── component_validation.md
│   │   ├── asset_validation.md
│   │   ├── monobehaviour_validation.md
│   │   ├── confidence_breakdown.md
│   │   ├── final_audit.md
│   │   ├── dependency_graph.html
│   │   └── scene_graph.html
│   ├── logs/                            # Phase M per-phase log files (phase_a.log, etc.)
│   ├── tests/                           # Pytest test suite (7/7 passing)
│   ├── cli.py                           # CLI Pipeline Orchestrator (supports --audit mode)
│   └── README.md                        # Documentation
```

---

## How to Run

### 1. Full Pipeline Execution
Execute the complete recovery and audit pipeline:
```bash
python3 -m recoverytool.cli
```

### 2. Dry-Run Audit Mode (`--audit`)
Run parsing, resolution, graph construction, validation, and report generation without rendering Unity C# code:
```bash
python3 -m recoverytool.cli --audit
```

### 3. Run Test Suite
Run unit tests with plugin autoload disabled:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest recoverytool/tests/
```

---

## How to Reconstruct Scene in Unity Editor

1. Open `cattersrecovered/assetripper/ExportedProject/` in Unity Editor.
2. Copy `recoverytool/generated/RecoverScene.cs` into `Assets/Editor/RecoverScene.cs`.
3. In Unity Editor menu bar, click **Tools -> Recover Scene**.
4. The script automatically recreates all GameObjects, sets active/static states, restores Transform/RectTransform hierarchy, attaches components, links meshes/materials/animator controllers, reconnects MonoBehaviours, and logs self-validation metrics in the Unity Console.
