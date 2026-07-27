# Information Loss Classification Report

Fidelity breakdown across the 5 information recovery tiers:

| Information Loss Tier | Object Count | Percentage | Description |
|---|---|---|---|
| **Recovered** | 1182 | **41.68%** | Exact data extracted directly from raw AssetStudio binary dump. |
| **Recovered by inference** | 32 | **1.13%** | Deduced from scene tree relationships and component type signatures. |
| **Recovered by matching** | 51 | **1.8%** | Matched by name & extension against ExportedProject .meta GUIDs. |
| **Missing** | 71 | **2.5%** | Assets or references that could not be resolved or matched. |
| **Impossible to recover** | 1500 | **52.89%** | Stripped or compiled-out data not preserved in raw asset bundles. |