using UnityEngine;

public class PlayerCollision : MonoBehaviour
{
	public PlayerMovement move;
	public Rigidbody rb;

	private void OnCollisionEnter(Collision collision)
	{
		string hitName = collision.collider.name;
		string hitTag = collision.collider.tag;
		Vector3 vel = rb != null ? rb.velocity : Vector3.zero;
		Debug.Log($"[PlayerCollision] Hit: name={hitName} tag={hitTag} vel={vel.ToString("F4")}");

		if (hitTag == "Obstacle")
		{
			if (move != null) move.enabled = false;
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
