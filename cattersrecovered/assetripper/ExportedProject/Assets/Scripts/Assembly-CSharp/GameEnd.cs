using UnityEngine;
using UnityEngine.UI;

public class GameEnd : MonoBehaviour
{
	public RawImage gameover;

	private void Update()
	{
		if (Object.FindObjectOfType<GameManager>().gameended)
		{
			Invoke("gameoverUItrig", 0.25f);
		}
	}

	private void gameoverUItrig()
	{
		gameover.enabled = true;
	}
}
