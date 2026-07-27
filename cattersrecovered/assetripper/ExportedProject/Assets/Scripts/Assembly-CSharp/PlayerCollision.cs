using UnityEngine;

public class PlayerCollision : MonoBehaviour
{
	public PlayerMovement move;
	public Rigidbody rb;

	private void OnCollisionEnter(Collision collision)
	{
		string hitName = collision.collider.name;
		string hitTag = collision.collider.tag;
		Debug.Log($"[PlayerCollision] Hit on Frame {Time.frameCount}: name={hitName} tag={hitTag} point={collision.contacts[0].point}");

		if (hitTag == "Obstacle")
		{
			if (move != null) move.enabled = false;
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
