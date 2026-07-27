using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
	public Rigidbody rb;

	public float ForwardForce = 50f;

	public float KeySideForce = 50f;

	public float ButtonSideForce = 50f;

	public MyButton left;

	public MyButton right;

	private void FixedUpdate()
	{
		rb.AddForce(base.transform.forward * ForwardForce * Time.deltaTime, ForceMode.VelocityChange);
		if (Input.GetKey("d"))
		{
			rb.AddForce(base.transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}
		if (Input.GetKey("a"))
		{
			rb.AddForce(-base.transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}
		if (right.isPressed)
		{
			rb.AddForce(base.transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}
		if (left.isPressed)
		{
			rb.AddForce(-base.transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}
		if (base.transform.localPosition.y < -1f)
		{
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
