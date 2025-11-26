import math
import numpy as np

def calculate_angle(landmark1, landmark2, landmark3):
    """
    计算三个标志点之间的角度。
    
    参数:
        landmark1: 第一个标志点，包含 x, y, z 坐标。
        landmark2: 第二个标志点，包含 x, y, z 坐标。
        landmark3: 第三个标志点，包含 x, y, z 坐标。
    
    返回值:
        angle: 三个标志点之间的角度。
    """
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    angle = abs(angle)
    
    return angle

def classify_posture(landmarks):
    """
    判断姿势是否为拘谨（1）或灵活（0）。
    
    参数:
        landmarks: 包含标志点的列表。
    
    返回值:
        result: 拘谨（1）或灵活（0），如果关键点有 NaN 则返回 None。
    """
    # 定义肩膀和肘部的索引
    left_hip_index, left_shoulder_index, left_elbow_index,  =  22, 12, 13
    right_hip_index, right_shoulder_index, right_elbow_index,  = 18, 5, 6

    # 检查关键点是否有 NaN 值
    key_indices = [left_shoulder_index, left_elbow_index, left_hip_index,
                   right_shoulder_index, right_elbow_index, right_hip_index]
    for index in key_indices:
        if np.any(np.isnan(landmarks[index])):
            return None  # 如果有 NaN，返回 None 表示跳过该人的判断

    # 计算肩膀夹角
    left_shoulder_angle = calculate_angle(landmarks[left_elbow_index],landmarks[left_shoulder_index], landmarks[left_hip_index])
    right_shoulder_angle = calculate_angle(landmarks[right_elbow_index], landmarks[right_shoulder_index], landmarks[right_hip_index])

    # 判断拘谨或灵活
    if left_shoulder_angle < 30 and right_shoulder_angle < 30:
        return 1  # 拘谨
    else:
        return 0  # 灵活
    
# def classify_all_person_postures(list_x):
#     """
#     对所有人进行姿势分类。
    
#     参数:
#         list_x: 包含所有人的列表。
    
#     返回值:
#         results: 每个人的姿势分类结果列表。
#     """
#     results = []
#     for person in list_x:
#         result = classify_posture(person['keypoint'])
#         if result is not None:
#             results.append({'id': person['id'], 'posture': result})
#     return results
