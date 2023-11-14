# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run a Flask REST API exposing one or more YOLOv5s models
"""

import argparse
import io
import os
import json
import numpy as np

import torch
from PIL import Image
from pathlib import Path
from flask import Flask, request, render_template, jsonify
from flask import abort
from traffic_inspector.main import TrafficInspector
from flask_cors import CORS

from traffic_inspector.helper import initialize_vision_objects
from roboflow import Roboflow
import torch
from ultralytics import YOLO


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

app = Flask(__name__)
CORS(app)
yolo_v5_model = torch.hub.load('ultralytics/yolov5', 'custom', path=ROOT / 'models/yolov5s_best_trained.pt')
DETECTION_URL = "/v1/object-detection/<model>"
# roboflow
# rf = Roboflow(api_key="HDll2oFm5X8KK35ziZJL")
# project = rf.workspace().project("smart-traffic-light")
# yolov8 = project.version(16).model

yolov8_model = YOLO(ROOT / 'models/yolov8_best_trained.pt')

models = {'yolov5': yolo_v5_model,
          'yolov8': yolov8_model}


@app.route(DETECTION_URL, methods=["POST"])
def predict(model):
    if request.method != "POST":
        return

    if not request.data:
        abort(400, "Bad request, image data is expected but not found in the request")

    im_bytes = request.data
    im = Image.open(io.BytesIO(im_bytes))

    if model == 'yolov8':
        yolov8_response = models['yolov8'].predict(im)
        predictions = []
        for pred in yolov8_response[0].boxes.data.numpy():
            pred_dict = {'xmin': np.float64(pred[0]),
                         'ymin': np.float64(pred[1]),
                         'xmax': np.float64(pred[2]),
                         'ymax': np.float64(pred[3]),
                         'confidence': np.float64(pred[4]),
                         'name': yolov8_response[0].names[pred[5]]}
            predictions.append(pred_dict)
        json_string = json.dumps(predictions)
        return json_string

    if model == 'yolov5':
        results = models['yolov5'](im, size=640)  # reduce size=320 for faster inference
        return results.pandas().xyxy[0].to_json(orient="records")


@app.route("/process_image", methods=["POST"])
def process_image():
    image_name = request.data.decode('utf-8')
    yolov8_response = models['yolov8'].predict(image_name)
    predictions = []
    for pred in yolov8_response[0].boxes.data.numpy():
        pred_dict = {'xmin': np.float64(pred[0]),
                     'ymin': np.float64(pred[1]),
                     'xmax': np.float64(pred[2]),
                     'ymax': np.float64(pred[3]),
                     'confidence': np.float64(pred[4]),
                     'name': yolov8_response[0].names[pred[5]]}
        predictions.append(pred_dict)
    json_string = json.dumps(predictions)
    return json_string


@app.route('/get_simulation_results')
def get_simulation_results():
    option = request.args.get('option')
    model_type = request.args.get('model_type')
    exec_mode = request.args.get('exec_mode')
    vision_list, close_vids = initialize_vision_objects(model_type, models[model_type])
    stl_1_dict = {'name': 'stl_1', 'status': 'green',
                  'vision_iter': vision_list[0], 'close_vids': close_vids[0]}
    stl_2_dict = {'name': 'stl_2', 'status': 'red',
                  'vision_iter': vision_list[1], 'close_vids': close_vids[1]}
    ti_obj = TrafficInspector([stl_1_dict, stl_2_dict], exec_mode)
    if option == 'option1':
        # For without AI scenario
        response = ti_obj.scheduled_version()
    else:
        # For with AI scenario
        response = ti_obj.run_simulation()

    return jsonify(response)

    # Below code is for testing the UI
    # data = {0: {'stl_1': {"status": 'red', "time_remaining": 30},
    #             'stl_2': {"status": 'green', "time_remaining": 30}},
    #         1: {'stl_1': {"status": 'green', "time_remaining": 30},
    #             'stl_2': {"status": 'red', "time_remaining": 30}},
    #         2: {'stl_1': {"status": 'red', "time_remaining": 30},
    #             'stl_2': {"status": 'green', "time_remaining": 30}}
    #         }
    # return jsonify(data)


@app.route('/upload', methods=["POST"])
def upload_video_file():
    base_path = 'static\\videos\\'
    file = request.files['file']
    filename = file.filename
    new_path = [dir.split('_')[-1] for dir in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, dir))][-1]
    new_path = os.path.join(base_path, f"scenario_{int(new_path) + 1}")
    abs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    if os.path.isdir(new_path) is False:
        os.makedirs(new_path)
    file.save(os.path.join(abs_path, new_path, filename))
    new_path = new_path.replace('\\', '/')
    file_url = f'{new_path}/{filename}'
    return jsonify({'fileUrl': file_url})


@app.route('/home')
def index():
    return render_template('home_page.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask API exposing YOLOv5 model")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    parser.add_argument('--model', nargs='+', default=['yolov5s'], help='model(s) to run, i.e. --model yolov5n yolov5s')
    opt = parser.parse_args()

    for m in opt.model:
        models[m] = torch.hub.load("ultralytics/yolov5", m, force_reload=True, skip_validation=True)

    app.run(host="0.0.0.0", port=opt.port, debug=True)  # debug=True causes Restarting with stat
