using System.Collections.Generic;
using UnityEngine;
using Rhino.Geometry;

public class SyncHead : MonoBehaviour
{
    UnityEngine.Quaternion previousHeadRotation; // 使用UnityEngine.Quaternion
    List<float> timeStamps = new List<float>();
    List<bool> isStationary = new List<bool>();
    float lastCalculationTime = 0.0f;
    float calculationInterval = 1.0f; // 每秒计算一次
    float stationaryAngleThreshold = 1.0f; // 静止状态角度阈值
    float timeWindow = 5.0f; // 计算静止状态的时间窗口
    float fixedDeltaTime = 1.0f; // 固定更新的时间间隔,1f/30f,1f/60f

    private void Start()
    {
        // 设置固定更新的频率
        Time.fixedDeltaTime = fixedDeltaTime;
    }

    private void FixedUpdate()
    {

        UnityEngine.Transform centerEyeAnchor = transform.Find("TrackingSpace/CenterEyeAnchor");
        
        if (centerEyeAnchor != null)
        {
            UnityEngine.Quaternion currentHeadRotation = centerEyeAnchor.rotation; // 使用UnityEngine.Quaternion

            if (previousHeadRotation != null)
            {
                float angleDifference = UnityEngine.Quaternion.Angle(previousHeadRotation, currentHeadRotation);
                bool stationary = angleDifference <= stationaryAngleThreshold;

                // 记录时间戳和静止状态
                timeStamps.Add(Time.time);
                isStationary.Add(stationary);

                // 如果时间间隔超过了设定的计算间隔，则计算静止状态占比
                if (Time.time - lastCalculationTime >= calculationInterval)
                {
                    CalculateAndSendStationaryPercentage();
                    lastCalculationTime = Time.time;
                }

                previousHeadRotation = currentHeadRotation;
            }
            else
            {
                previousHeadRotation = currentHeadRotation;
            }

            Debug.Log("Head Rotation: " + currentHeadRotation);
            SendHeadRotation(centerEyeAnchor.position, currentHeadRotation);
        }
    }


    private void CalculateAndSendStationaryPercentage()
    {
        float currentTime = Time.time;

        // 移除时间窗口之外的记录
        while (timeStamps.Count > 0 && timeStamps[0] < currentTime - timeWindow)
        {
            timeStamps.RemoveAt(0);
            isStationary.RemoveAt(0);
        }

        // 计算静止状态占比
        int stationaryCount = 0;
        foreach (bool stationary in isStationary)
        {
            if (stationary) stationaryCount++;
        }

        float stationaryPercentage = (float)stationaryCount / isStationary.Count * 100;
        Debug.Log("Stationary Percentage in the last 5 seconds: " + stationaryPercentage + "%");
        // 将静止状态百分比发送到 Rhino Inside Unity
        SendStationaryPercentage(stationaryPercentage);
    }

    public void SendHeadRotation(Vector3 position, UnityEngine.Quaternion rotation) // 使用UnityEngine.Quaternion
    {
        using (var args = new Rhino.Runtime.NamedParametersEventArgs())
        {
            // 将四元数转换为欧拉角                                                                                    
            Vector3 eulerAngles = rotation.eulerAngles;
            // 转换 Unity Vector3 和 Quaternion 到 Rhino 的 Point3d 和 Vector3d
            Rhino.Geometry.Point3d positionRhino = new Rhino.Geometry.Point3d(position.x, position.z, position.y); // 注意：Unity 和 Rhino 的坐标系可能不同
            Rhino.Geometry.Vector3d rotationRhino = new Rhino.Geometry.Vector3d(eulerAngles.x, eulerAngles.y, eulerAngles.z);
            //Rhino.Geometry.Quaternion rotationRhino = new Rhino.Geometry.Quaternion(rotation.x, rotation.y, rotation.z, rotation.w);


            args.Set("HeadPosition", positionRhino);
            args.Set("HeadRotation", rotationRhino);
            Rhino.Runtime.HostUtils.ExecuteNamedCallback("ToGH_HeadPose", args);
        }
    }

    public void SendStationaryPercentage(float percentage)
    {
        using (var args = new Rhino.Runtime.NamedParametersEventArgs())
        {
            args.Set("StationaryPercentage", percentage);
            Rhino.Runtime.HostUtils.ExecuteNamedCallback("ToGH_StationaryPercentage", args);
        }
    }
}
