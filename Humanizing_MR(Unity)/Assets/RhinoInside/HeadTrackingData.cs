using UnityEngine;
using UnityEngine.XR;

public class HeadTrackingData : MonoBehaviour
{
    private void Update()
    {
        // Get the head position and rotation from the center eye anchor
        Transform centerEyeAnchor = transform.Find("TrackingSpace/CenterEyeAnchor");

        if (centerEyeAnchor != null)
        {
            Vector3 headPosition = centerEyeAnchor.position;
            Quaternion headRotation = centerEyeAnchor.rotation;

            Debug.Log("Head Position: " + headPosition);
            Debug.Log("Head Rotation: " + headRotation);

            // Optional: Use the data here or send it to another application
            // SendDataToExternalApplication(headPosition, headRotation);
        }
    }
}
