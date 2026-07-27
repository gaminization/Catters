using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
	public Rigidbody rb;
	public float ForwardForce = 0.25f;
	public float KeySideForce = 1f;
	public float ButtonSideForce = 1f;
	public MyButton left;
	public MyButton right;

	private int frameCount = 0;

	private void Awake()
	{
		if (rb == null) rb = GetComponent<Rigidbody>();
	}

	private void FixedUpdate()
	{
		if (rb == null) rb = GetComponent<Rigidbody>();

		frameCount++;
		Vector3 velBefore = rb != null ? rb.velocity : Vector3.zero;

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

		Vector3 velAfter = rb != null ? rb.velocity : Vector3.zero;

		if (frameCount <= 10 || frameCount % 30 == 0)
		{
			Debug.Log($"[PlayerMovement #{frameCount}] Pos={transform.position.ToString("F4")} VelBefore={velBefore.ToString("F4")} VelAfter={velAfter.ToString("F4")}");
		}

		if (transform.localPosition.y < -1f)
		{
			Object.FindObjectOfType<GameManager>().EndGame();
		}
	}
}
