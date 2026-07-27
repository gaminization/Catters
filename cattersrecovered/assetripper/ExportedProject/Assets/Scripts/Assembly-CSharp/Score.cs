using TMPro;
using UnityEngine;

public class Score : MonoBehaviour
{
	public TextMeshProUGUI scoreText;

	public Transform player;

	private void Update()
	{
		scoreText.text = player.position.z.ToString("0");
	}
}
