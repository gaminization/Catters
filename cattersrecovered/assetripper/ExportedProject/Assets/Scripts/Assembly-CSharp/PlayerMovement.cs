using System.Collections;
using System.Collections.Generic;
using TMPro;
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
		if (rb != null)
		{
			rb.AddForce(transform.forward * ForwardForce * Time.deltaTime, ForceMode.VelocityChange);
		}

		if (Input.GetKey("d"))
		{
			if (rb != null) rb.AddForce(transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}

		if (Input.GetKey("a"))
		{
			if (rb != null) rb.AddForce(-transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}

		if (right != null && right.isPressed)
		{
			if (rb != null) rb.AddForce(transform.right * ButtonSideForce * Time.deltaTime, ForceMode.VelocityChange);
		}

		if (left != null && left.isPressed)
		{
			if (rb != null) rb.AddForce(-transform.right * KeySideForce * Time.deltaTime, ForceMode.VelocityChange);
		}

		if (transform.localPosition.y < -1f)
		{
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
