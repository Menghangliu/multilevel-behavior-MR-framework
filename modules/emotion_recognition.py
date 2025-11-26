import time
import numpy as np
import cv2
import os
import threading
from google.cloud import vision
from google.oauth2 import service_account

import pyzed.sl as sl
from collections import deque
import socket

# 配置代理（如果需要）
os.environ['http_proxy'] = 'http://127.0.0.1:52031'
os.environ['https_proxy'] = 'http://127.0.0.1:52031'

# Google Cloud Vision API 配置
credentials = service_account.Credentials.from_service_account_file(
    './linear-arcadia-428108-u4-77ca8a070ab6.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
client = vision.ImageAnnotatorClient(credentials=credentials)

def likelihood_to_number(likelihood):
    return {
        vision.Likelihood.UNKNOWN: 0,
        vision.Likelihood.VERY_UNLIKELY: 1,
        vision.Likelihood.UNLIKELY: 2,
        vision.Likelihood.POSSIBLE: 3,
        vision.Likelihood.LIKELY: 4,
        vision.Likelihood.VERY_LIKELY: 5
    }[likelihood]

def detect_face_expressions_from_frame(frame, callback):
    _, encoded_image = cv2.imencode('.jpg', frame)
    content = encoded_image.tobytes()
    vision_image = vision.Image(content=content)
    response = client.face_detection(image=vision_image)
    faces = response.face_annotations
    results = []
    expression_sums = {"Joy": 0, "Sorrow": 0, "Anger": 0, "Surprise": 0}
    max_headwear_likelihood = 0
    expression_on_headwearer = {}

    for face in faces:
        expressions = {
            "Joy": likelihood_to_number(face.joy_likelihood),
            "Sorrow": likelihood_to_number(face.sorrow_likelihood),
            "Anger": likelihood_to_number(face.anger_likelihood),
            "Surprise": likelihood_to_number(face.surprise_likelihood),
            "Headwear": likelihood_to_number(face.headwear_likelihood)
                }
        results.append((face.bounding_poly, expressions))
        for key in expression_sums:
            expression_sums[key] += expressions[key]
        
        # 找到 headwearLikelihood 最大且大于 2 的人
        if face.headwear_likelihood > max_headwear_likelihood and face.headwear_likelihood >= 2:
            max_headwear_likelihood = face.headwear_likelihood
            expression_on_headwearer = expressions

    if faces:
        expression_averages = {key: (value / len(faces)) for key, value in expression_sums.items()}
    else:
        expression_averages = {key: 1 for key in expression_sums} #revised
    
    callback(results, expression_averages, expression_on_headwearer)

def async_detect_and_update(frame, expressions_list, expression_averages, expression_on_headwearer):
    def callback(results, averages, headwearer_expression):
        expressions_list.clear()
        expressions_list.extend(results)
        
        expression_averages.clear()
        expression_averages.update(averages)
        
        expression_on_headwearer.clear()
        expression_on_headwearer.update(headwearer_expression)
        # print("Averages: ", expression_averages)
        # print("Headwearer Expressions: ", expression_on_headwearer)

    detect_face_expressions_from_frame(frame, callback)

def draw_expression_on_frame(frame, bounding_poly, expression_dict, show_labels):
    vertices = [(vertex.x, vertex.y) for vertex in bounding_poly.vertices]
    x_min = min(vertices, key=lambda x: x[0])[0]
    y_min = min(vertices, key=lambda x: x[1])[1]
    x_max = max(vertices, key=lambda x: x[0])[0]
    y_max = max(vertices, key=lambda x: x[1])[1]
    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    if show_labels:
        expression_text = ', '.join([f'{exp}: {likelihood}' for exp, likelihood in expression_dict.items()])
        cv2.putText(frame, expression_text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


        