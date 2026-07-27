using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
	public bool gameended;

	public void EndGame()
	{
		if (!gameended)
		{
			gameended = true;
			Debug.Log("game over");
			Invoke("Restart", 5f);
		}
	}

	private void Restart()
	{
		SceneManager.LoadScene(SceneManager.GetActiveScene().name);
	}
}
