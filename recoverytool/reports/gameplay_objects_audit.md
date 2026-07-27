# Gameplay Objects Audit Report

Audit of requested gameplay objects (`Player`, `GameManager`, `Main Camera`, etc.):

| Object Name | Present in Raw Dump (`objects.json`) | Present in `scene.json` | Emitted into `RecoverScene.cs` | Status / Findings |
|---|---|---|---|---|
| `Player` | No | No | No | Not present in raw AssetStudio dump bundle (level scene dump). |
| `GameManager` | No | No | No | Not present in raw AssetStudio dump bundle (level scene dump). |
| `Main Camera` | No | No | No | Not present in raw AssetStudio dump bundle (level scene dump). |
| `Canvas` | Yes | Yes | Yes | Fully emitted and reconstructed with RectTransform & Canvas. |
| `Directional Light` | Yes | Yes | Yes | Fully emitted and reconstructed with Light component. |
| `Clouds` / `Fences` / `Obstacles` | Yes | Yes | Yes | All 137 GameObjects in raw dump are 100% emitted. |