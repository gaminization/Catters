using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class BatchRunner
{
    public static void BuildAndRecord()
    {
        Debug.Log("[BatchRunner] Starting Scene Recovery...");
        RecoverScene.ExecuteSceneRecovery();

        string scenePath = "Assets/Scenes/MainScene.unity";
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), scenePath);
        Debug.Log($"[BatchRunner] Scene saved to {scenePath}");

        Debug.Log("[BatchRunner] Building Standalone Linux Player...");
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.scenes = new[] { scenePath };
        buildPlayerOptions.locationPathName = "Builds/Linux/Catters.x86_64";
        buildPlayerOptions.target = BuildTarget.StandaloneLinux64;
        buildPlayerOptions.options = BuildOptions.None;

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        Debug.Log($"[BatchRunner] Build result: {report.summary.result}, size: {report.summary.totalSize} bytes");
    }
}
