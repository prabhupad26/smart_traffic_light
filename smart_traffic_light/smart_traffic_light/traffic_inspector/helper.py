import os
import json
import numpy as np

from PIL import Image, ImageDraw
from smart_traffic_light.traffic_inspector.infer_cv_api import Lane


def initialize_vision_objects(model_type, model_obj):
    input_data_path = "static\\videos\\scenario_1"
    output_data_path = "static\\videos_processed\\scenario_1"
    input_data_path = os.path.join(os.getcwd(), input_data_path)
    with open(os.path.join(input_data_path, 'user1_inputs.json')) as cf:
        config_files = json.load(cf)

    # build lanes
    lanes = []
    lane_props_dict = config_files.get("initial_conditions").get("lane_props")
    if lane_props_dict:
        for lane_id, lane_props in lane_props_dict.items():
            if lane_props['video_feed']:
                video_path = os.path.join(input_data_path, lane_props['video_feed'])
                lanes.append(Lane(int(lane_id), model_obj, lane_props['status'], lane_props['lane_type']['direction'],
                                  lane_props['lane_type']['exit'], video_path, model_type,
                                  output_data_path))
            # TODO : Build logic to support all scenarios
    else:
        print("No lanes configured by user")

    compare_lanes = [lane.get_element_count() for lane in lanes if lane.number in [1, 2]]
    close_vids = [lane.reset for lane in lanes]
    return compare_lanes, close_vids


def draw_boxes(box, x0, y0, img, class_name):
    # OPTIONAL - color map, change the key-values for each color to make the
    # class output labels specific to your dataset
    color_map = {
        "car": "red",
        "ambulance": "blue",
        "transport_vehicle": "yellow",
        "firetruck": "green",
        "police_car": "black",
        "motorbike": "grey"
    }

    # get position coordinates
    bbox = ImageDraw.Draw(img)

    bbox.rectangle(box, outline=color_map[class_name], width=5)
    bbox.text((x0, y0), class_name, fill='black', anchor='mm')

    return img


def save_with_bbox_renders(img):
    output_data_path = "static\\videos\\scenario_1_image_mode\\output"
    output_data_path = os.path.join(os.getcwd(), output_data_path)
    file_name = os.path.basename(img.filename)
    img.save(os.path.join(output_data_path, file_name))

