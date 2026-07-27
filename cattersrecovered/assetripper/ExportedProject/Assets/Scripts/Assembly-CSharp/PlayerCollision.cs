using UnityEngine;

public class PlayerCollision : MonoBehaviour
{
	public PlayerMovement move;

	public Rigidbody rb;

	private void OnCollisionEnter(Collision collision)
	{
		if (collision.collider.tag == "Obstacle")
		{
			move.enabled = false;
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
