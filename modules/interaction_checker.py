import numpy as np

def quaternion_to_axis(quaternion):
    """
    从四元数中提取旋转轴（法向量）

    参数:
    quaternion (list or np.ndarray): 四元数 [x, y, z, w]

    返回值:
    np.ndarray: 旋转轴（法向量） [x, y, z]
    """
    x, y, z = quaternion[0], quaternion[1], quaternion[2]
    norm = np.sqrt(x**2 + y**2 + z**2)
    if norm == 0:
        return np.array([0, 0, 0])
    axis = np.array([x / norm, y / norm, z / norm])
    return axis

def calculate_head_vector_from_bbox(head_bounding_box):
    """
    从头部 bounding box 计算头部向量

    参数:
    head_bounding_box (list): 头部 bounding box 的 8 个数组

    返回值:
    np.ndarray: 计算出来的头部向量
    """
    # 假设头部 bounding box 的 8 个点按照某种顺序排列,例如：
    # 前四个点是bounding box的前面四个角
    # 后四个点是bounding box的后面四个角
    
    front_center = np.mean(head_bounding_box[:4], axis=0)
    back_center = np.mean(head_bounding_box[4:], axis=0)
    head_vector = front_center - back_center
    head_vector = head_vector / np.linalg.norm(head_vector)
    
    return head_vector

def extract_person_data(person):
    """
    提取人的数据并计算法向量

    参数:
    person (dict): 包含人的数据的字典

    返回值:
    tuple: (id, position, normal_vector)
    """
    person_id = person['id']
    person_position = np.array(person['position'])
    person_global_root_orientation = person['global_root_orientation']
    person_normal_vector = quaternion_to_axis(person_global_root_orientation)

    person_head_bounding_box = person['head_bounding_box']
    person_head_position = np.array(person['head_position'])
    person_head_normal_vector = calculate_head_vector_from_bbox(person_head_bounding_box)
    

    return person_id, person_position, person_global_root_orientation, person_normal_vector, person_head_bounding_box, person_head_position, person_head_normal_vector

def check_interaction(list_x):
    interaction_result = None

    # 检查人数
    if len(list_x) <= 1:
        interaction_result = 0
    elif len(list_x) > 2:
        interaction_result = 1
    elif len(list_x) == 2:
        # 提取第一个人的数据
        person1_id, person1_position, person1_normal_vector, person1_global_root_orientation, person1_head_bounding_box, person1_head_position, person1_head_normal_vector = extract_person_data(list_x[0])
        
        # 提取第二个人的数据
        person2_id, person2_position, person2_normal_vector, person2_global_root_orientation, person2_head_bounding_box, person2_head_position, person2_head_normal_vector = extract_person_data(list_x[1])
        
        # 计算距离
        distance = np.linalg.norm(person1_position - person2_position)
        # distance = np.linalg.norm(person1_head_position - person2_head_position)
        
        # 计算法向量夹角
        dot_product = np.dot(person1_normal_vector / np.linalg.norm(person1_normal_vector), 
                            person2_normal_vector / np.linalg.norm(person2_normal_vector))
        angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))

        # dot_product = np.dot(person1_head_normal_vector / np.linalg.norm(person1_head_normal_vector), 
        #                     person2_head_normal_vector / np.linalg.norm(person2_head_normal_vector))
        # angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))
        print('distance:',distance,'angle:',angle)
        # 判断条件
        if angle < 120 : #and distance > 1:
            interaction_result = 0
        else:
            interaction_result = 1

    return interaction_result

def check_interaction_using_head(list_x):
    interaction_result = None

    # 检查人数
    if len(list_x) <= 1:
        interaction_result = 0
    elif len(list_x) > 2:
        interaction_result = 1
    elif len(list_x) == 2:
        # 提取第一个人的数据
        person1_id, person1_position, person1_normal_vector, person1_head_bounding_box, person1_head_position, person1_head_normal_vector = extract_person_data(list_x[0])
        
        # 提取第二个人的数据
        person2_id, person2_position, person2_normal_vector, person2_head_bounding_box, person2_head_position, person2_head_normal_vector = extract_person_data(list_x[1])
        
        # 计算距离
        # distance = np.linalg.norm(person1_position - person2_position)
        distance = np.linalg.norm(person1_head_position - person2_head_position)
        
        # 计算法向量夹角
        # dot_product = np.dot(person1_normal_vector / np.linalg.norm(person1_normal_vector), 
        #                     person2_normal_vector / np.linalg.norm(person2_normal_vector))
        # angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))

        dot_product = np.dot(person1_head_normal_vector / np.linalg.norm(person1_head_normal_vector), 
                            person2_head_normal_vector / np.linalg.norm(person2_head_normal_vector))
        angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))
        
        # 判断条件
        if angle < 120 and distance > 1:
            interaction_result = 0
        else:
            interaction_result = 1

    return interaction_result