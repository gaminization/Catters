# Dropped Serialized Properties Audit Report

Comparing canonical `database/scene.json` against generated C# `RecoverScene.cs`:

| Property Name | Component Type | Reason for Omission / Handling |
|---|---|---|
| `byteSize` | All | Binary serialization metadata, not exposed in Unity C# runtime API. |
| `classID` | All | Internal Unity class identifier, handled by component creation. |
| `m_PathID` | All | Internal serialization PathID, mapped via createdObjects index. |
| `m_Father` | Transform / RectTransform | Represented by `transform.SetParent(parent, false)`. |
| `m_Children` | Transform / RectTransform | Represented by tree hierarchy traversal. |
| `m_StaticBatchInfo` | MeshRenderer | Handled automatically by Unity batching pipeline. |
| `m_SubsetIndices` | MeshRenderer | Internal submesh indexing, computed from Mesh asset. |