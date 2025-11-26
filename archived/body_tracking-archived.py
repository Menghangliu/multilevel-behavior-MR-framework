########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
   This sample shows how to detect a human bodies and draw their 
   modelised skeleton in an OpenGL window
"""
import cv2
import sys
import pyzed.sl as sl
import ogl_viewer.viewer as gl
import cv_viewer.tracking_viewer as cv_viewer
import numpy as np
import argparse
import json
import socket
import time

import modules.interaction_checker as ic
import modules.posture_checker as pc
import modules.emotion_recognition as er

import os
import threading
from google.cloud import vision
from google.oauth2 import service_account

# Google Vision相关
# os.environ['http_proxy'] = 'http://127.0.0.1:52031'
# os.environ['https_proxy'] = 'http://127.0.0.1:52031'

# credentials = service_account.Credentials.from_service_account_file(
#     './bustling-wharf-359411-b33e8c55e506.json',
#     scopes=['https://www.googleapis.com/auth/cloud-platform']
# )
# client = vision.ImageAnnotatorClient(credentials=credentials)

# Function to send keypoints over UDP
def send_keypoints_over_udp(keypoints, host, port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (host, port)

    try:
        # Convert keypoints to bytes
        keypoints_bytes = keypoints.encode()

        # Send keypoints over UDP
        sock.sendto(keypoints_bytes, server_address)
        # print("Keypoints sent successfully.")
    except Exception as e:
        print(f"Error sending data: {e}")
    finally:
        sock.close()

def addIntoOutput(out, identifier, tab):
    out[identifier] = []
    for element in tab:
        out[identifier].append(element)
    return out

def serializeBodyData(body_data):
    """Serialize BodyData into a JSON like structure"""
    out = {}
    out["id"] = body_data.id
    out["unique_object_id"] = str(body_data.unique_object_id)
    out["tracking_state"] = str(body_data.tracking_state)
    out["action_state"] = str(body_data.action_state)
    addIntoOutput(out, "position", body_data.position)
    addIntoOutput(out, "velocity", body_data.velocity)
    addIntoOutput(out, "bounding_box_2d", body_data.bounding_box_2d)
    out["confidence"] = body_data.confidence
    addIntoOutput(out, "bounding_box", body_data.bounding_box)
    addIntoOutput(out, "dimensions", body_data.dimensions)
    addIntoOutput(out, "keypoint_2d", body_data.keypoint_2d)
    addIntoOutput(out, "keypoint", body_data.keypoint)
    addIntoOutput(out, "keypoint_cov", body_data.keypoints_covariance)
    addIntoOutput(out, "head_bounding_box_2d", body_data.head_bounding_box_2d)
    addIntoOutput(out, "head_bounding_box", body_data.head_bounding_box)
    addIntoOutput(out, "head_position", body_data.head_position)
    addIntoOutput(out, "keypoint_confidence", body_data.keypoint_confidence)
    addIntoOutput(out, "local_position_per_joint", body_data.local_position_per_joint)
    addIntoOutput(out, "local_orientation_per_joint", body_data.local_orientation_per_joint)
    addIntoOutput(out, "global_root_orientation", body_data.global_root_orientation)
    return out

def serializeBodies(bodies):
    """Serialize Bodies objects into a JSON like structure"""
    out = {}
    out["is_new"] = bodies.is_new
    out["is_tracked"] = bodies.is_tracked
    out["timestamp"] = bodies.timestamp.data_ns
    out["body_list"] = []
    for sk in bodies.body_list:
        out["body_list"].append(serializeBodyData(sk))
    return out

def parse_args(init):
    if len(opt.input_svo_file)>0 and opt.input_svo_file.endswith(".svo"):
        init.set_from_svo_file(opt.input_svo_file)
        print("[Sample] Using SVO File input: {0}".format(opt.input_svo_file))
    elif len(opt.ip_address)>0 :
        ip_str = opt.ip_address
        if ip_str.replace(':','').replace('.','').isdigit() and len(ip_str.split('.'))==4 and len(ip_str.split(':'))==2:
            init.set_from_stream(ip_str.split(':')[0],int(ip_str.split(':')[1]))
            print("[Sample] Using Stream input, IP : ",ip_str)
        elif ip_str.replace(':','').replace('.','').isdigit() and len(ip_str.split('.'))==4:
            init.set_from_stream(ip_str)
            print("[Sample] Using Stream input, IP : ",ip_str)
        else :
            print("Unvalid IP format. Using live stream")
    if ("HD2K" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD2K
        print("[Sample] Using Camera in resolution HD2K")
    elif ("HD1200" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD1200
        print("[Sample] Using Camera in resolution HD1200")
    elif ("HD1080" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD1080
        print("[Sample] Using Camera in resolution HD1080")
    elif ("HD720" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD720
        print("[Sample] Using Camera in resolution HD720")
    elif ("SVGA" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.SVGA
        print("[Sample] Using Camera in resolution SVGA")
    elif ("VGA" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.VGA
        print("[Sample] Using Camera in resolution VGA")
    elif len(opt.resolution)>0: 
        print("[Sample] No valid resolution entered. Using default")
    else : 
        print("[Sample] Using default resolution")

# expressions_list = []
# expression_averages = {}
# expression_on_headwearer = {}
# last_api_call_time = time.time()
# image_left_ocv = None  # 用于存储图像数据
# udp_server_host = '100.78.20.208' 

# def api_call_loop():
#     global last_api_call_time, image_left_ocv
#     while True:
#         current_time = time.time()
#         if current_time - last_api_call_time >= 1:
#             last_api_call_time = current_time
#             start_time = time.time()
#             threading.Thread(target=er.async_detect_and_update, args=(image_left_ocv, expressions_list, expression_averages, expression_on_headwearer)).start()
#             end_time = time.time()
#             print(f"async_detect_and_update took {end_time - start_time:.2f} seconds")
            
#             # 发送表情数据到UDP
#             er.send_keypoints_over_udp(str(expression_averages), udp_server_host, 405)
#             er.send_keypoints_over_udp('\n'.join([f"{key}:{value}" for key, value in expression_on_headwearer.items()]), udp_server_host, 403)
#             er.send_keypoints_over_udp('\n'.join([f"{key}:{value}" for key, value in expression_averages.items()]), udp_server_host, 402)
#         time.sleep(0.1)  # 确保API调用线程频率

# # 启动API调用线程
# api_thread = threading.Thread(target=api_call_loop)
# api_thread.start()

def main():
    print("Running Body Tracking sample ... Press 'q' to quit, or 'm' to pause or restart")

    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
    init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP  # Set coordinate system, 但是这样的话骨骼画面就没有显示到TBD
    
    parse_args(init_params)

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances
    # positional_tracking_parameters.set_as_static = True
    # Set the initial position of the Camera Frame at 1m80 above the World Frame
    initial_position = sl.Transform()
    initial_translation = sl.Translation()
    # initial_translation.init_vector(0, 0, 1.8)  # 1.8 meters above the world frame
    initial_position.set_translation(initial_translation)
    positional_tracking_parameters.set_initial_world_transform(initial_position)
    zed.enable_positional_tracking(positional_tracking_parameters)
    camera_pose = sl.Pose()

    body_param = sl.BodyTrackingParameters()
    body_param.enable_tracking = True                # Track people across images flow
    body_param.enable_body_fitting = False            # Smooth skeleton move
    body_param.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST 
    body_param.body_format = sl.BODY_FORMAT.BODY_34  # Choose the BODY_FORMAT you wish to use
    zed.enable_body_tracking(body_param)

    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 40

    # Get ZED camera information
    camera_info = zed.get_camera_information()

    # 2D viewer utilities
    display_resolution = sl.Resolution(min(camera_info.camera_configuration.resolution.width, 1280), min(camera_info.camera_configuration.resolution.height, 720))
    image_scale = [display_resolution.width / camera_info.camera_configuration.resolution.width
                 , display_resolution.height / camera_info.camera_configuration.resolution.height]

    # Create OpenGL viewer
    viewer = gl.GLViewer()
    viewer.init(camera_info.camera_configuration.calibration_parameters.left_cam, body_param.enable_tracking,body_param.body_format)
    
    # Create ZED objects filled in the main loop
    bodies = sl.Bodies()
    image = sl.Mat()
    
    key_wait = 10 
    expressions_list = []
    expression_averages = {}
    expression_on_headwearer = {}
    last_api_call_time = time.time()
    # Define the UDP server address and port
    udp_server_host = '100.78.20.208'       #'100.78.20.208'   # Change this to the server IP address
    # udp_server_port = 11111                 # Change this to the desired port number


    # 验证初始位置
    zed.get_position(camera_pose, sl.REFERENCE_FRAME.WORLD)
    initial_translation = camera_pose.get_translation(sl.Translation()).get()
    print(f"Initial Camera Position (World Coordinate System): {initial_translation}")

    while viewer.is_available():
        # Grab an image
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Get the camera pose
            zed.get_position(camera_pose, sl.REFERENCE_FRAME.WORLD)
            # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
            # Retrieve bodies
            zed.retrieve_bodies(bodies, body_runtime_param)
            # Update GL view
            viewer.update_view(image, bodies) 
            # Update OCV view
            image_left_ocv = image.get_data()
            cv_viewer.render_2D(image_left_ocv,image_scale, bodies.body_list, body_param.enable_tracking, body_param.body_format)
            
            # skeleton_file_data = {}
            # skeleton_file_data[str(bodies.timestamp.get_milliseconds())] = serializeBodies(bodies)

            # Print the position and orientation
            # translation = camera_pose.get_translation(sl.Translation()).get()
            # orientation = camera_pose.get_orientation().get()
            # print(f"Position (World Coordinate System): {translation}, Orientation: {orientation}")


            out = {}
            out = serializeBodies(bodies)
            list_x = out['body_list']

            # print(type(bodies))
            # print(type(list_x))

            text_data = ""
            text_data2 = ""
            for entry in list_x:
                person_id = entry['id']
                keypoint_data = entry['keypoint']
                keypoint_data = np.nan_to_num(keypoint_data, nan=0)
                reshaped_array = keypoint_data.reshape(-1, 3)
                person_data = f"Person {person_id}:\n"
                for row in reshaped_array:
                    person_data += " ".join([str(elem) for elem in row]) + "\n"
                text_data += person_data + "\n"

                person_id, person_position, person_global_root_orientation, person_normal_vector, person_head_bounding_box, person_head_position, person_head_normal_vector = ic.extract_person_data(entry)
                person_data_str = (
                    f"ID:{person_id}\n"
                    f"Position:{' '.join(map(str, person_position))}\n"
                    f"Global Root Orientation:{' '.join(map(str, person_global_root_orientation))}\n"
                    # f"Normal Vector: {person_normal_vector}\n"
                    f"Head Position:{' '.join(map(str, person_head_position))}\n"  
                    f"Head Bounding Box:\n" + 
                    "\n".join([f"{' '.join(map(str, bbox_point))}" for bbox_point in person_head_bounding_box]) + "\n\n" 
                )
                text_data2 += person_data_str

            send_keypoints_over_udp(text_data, udp_server_host, 1111)
            # send_keypoints_over_udp(text_data2, udp_server_host, 2222)

            

            # if list_x:  
                # ''' 调用函数判断交往状态，还有点问题to check,但是现在不这样判断了'''
                # interaction_result = ic.check_interaction(list_x)
                # interaction_result_using_head = ic.check_interaction_using_head(list_x)
                # send_keypoints_over_udp(str(interaction_result), udp_server_host, 100)
                # send_keypoints_over_udp(str(interaction_result_using_head), udp_server_host, 101)
                # send_keypoints_over_udp(str(len(list_x)), udp_server_host, 102)
                

                # ''' 调用函数判断任务处理模式，1 - 拘谨， 暂时：对随机一个人 '''
                # posture_result = pc.classify_posture(list_x[0]['keypoint'])
                # # print(posture_result)
                # send_keypoints_over_udp(str(posture_result), udp_server_host, 200)

            # ''' 调用google vision api返回表情，会卡，不要用'''
            # results, averages = detect_face_expressions_from_frame(image_left_ocv)
            # print(f"Results: {results}, Averages: {averages}")
            # send_keypoints_over_udp(str(results), udp_server_host, 400)

            current_time = time.time()
            if current_time - last_api_call_time >= 1: #返回结果时间间隔
                last_api_call_time = current_time
                start_time = time.time()
                threading.Thread(target=er.async_detect_and_update, args=(image_left_ocv, expressions_list, expression_averages,expression_on_headwearer)).start()
                end_time = time.time()
                print(f"async_detect_and_update took {end_time - start_time:.2f} seconds")

                
                print(expression_averages)

            send_keypoints_over_udp(str(expression_averages),udp_server_host, 405)
            send_keypoints_over_udp('\n'.join([f"{key}:{value}" for key, value in expression_on_headwearer.items()]), udp_server_host, 403)
            send_keypoints_over_udp('\n'.join([f"{key}:{value}" for key, value in expression_averages.items()]), udp_server_host, 402)

            if expressions_list:
                for bounding_poly, expression_dict in expressions_list:
                    er.draw_expression_on_frame(image_left_ocv, bounding_poly, expression_dict, True)

                # for _, expression_dict in expressions_list:
                #     formatted_expression_data = '\n'.join([f"{key}:{value}" for key, value in expression_dict.items()])
                #     send_keypoints_over_udp(formatted_expression_data, udp_server_host, 4444)

            cv2.imshow("ZED | 2D View", image_left_ocv)
            key = cv2.waitKey(key_wait)
            if key == 113: # for 'q' key
                print("Exiting...")
                break
            if key == 109: # for 'm' key
                if (key_wait>0):
                    print("Pause")
                    key_wait = 0 
                else : 
                    print("Restart")
                    key_wait = 10 
    viewer.exit()
    image.free(sl.MEM.CPU)
    zed.disable_body_tracking()
    zed.disable_positional_tracking()
    zed.close()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_svo_file', type=str, help='Path to an .svo file, if you want to replay it',default = '')
    parser.add_argument('--ip_address', type=str, help='IP Adress, in format a.b.c.d:port or a.b.c.d, if you have a streaming setup', default = '')
    parser.add_argument('--resolution', type=str, help='Resolution, can be either HD2K, HD1200, HD1080, HD720, SVGA or VGA', default = '')
    opt = parser.parse_args()
    if len(opt.input_svo_file)>0 and len(opt.ip_address)>0:
        print("Specify only input_svo_file or ip_address, or none to use wired camera, not both. Exit program")
        exit()
    main() 