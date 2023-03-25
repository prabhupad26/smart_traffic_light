import json
import os
import time
from typing import List, AnyStr, ByteString
import sys
import numpy as np

import cv2
import requests


class Lane:
    def __init__(self, number: int, model_obj, status: AnyStr = None, direction: AnyStr = None,
                 exit_lane: List = None, video_file: AnyStr = None, model_type: AnyStr = None,
                 output_data_path: AnyStr = None) -> None:
        self.number = number
        self.status = status
        self.direction = direction
        self.exit_lane = exit_lane
        self.model = model_obj
        self.video = cv2.VideoCapture(video_file)
        fps = self.video.get(cv2.CAP_PROP_FPS)
        width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

        self.out = cv2.VideoWriter(os.path.join(output_data_path,
                                                os.path.basename(video_file)),
                                   codec, fps, (int(width),
                                                int(height)))
        self.model_type = model_type

    def get_frame(self):
        """
        This generator will generate the bytestream object frame by frame
        """
        while self.video.isOpened():
            resp_json =None
            for frame_num in range(int(self.video.get(cv2.CAP_PROP_FPS))):
                success, frame = self.video.read()
                if success is True:
                    resp_json = self.infer_offline_model(frame)
                else:
                    print("End of video")
                    break
            yield resp_json

    @staticmethod
    def process_yolov8_response(yolov8_response):
        predictions = []
        for pred in yolov8_response[0].boxes.data.numpy():
            pred_dict = {'xmin': np.float64(pred[0]),
                         'ymin': np.float64(pred[1]),
                         'xmax': np.float64(pred[2]),
                         'ymax': np.float64(pred[3]),
                         'confidence': np.float64(pred[4]),
                         'name': yolov8_response[0].names[pred[5]]}
            predictions.append(pred_dict)
        return predictions

    def infer_offline_model(self, frame):
        if self.model_type == "yolov8":
            output = self.model(frame, imgsz=700)
            self.out.write(output[0].plot())
            return self.process_yolov8_response(output)
        return None

    def get_element_count(self) -> int:
        """
        Generator to collect the detected traffic elements frame by frame
        """
        for response_json in self.get_frame():
            if response_json:
                traffic_details = {}
                for items in response_json:
                    key_name = 'name' if 'name' in items else 'class'
                    if items[key_name] not in traffic_details:
                        traffic_details[items[key_name]] = 0
                    traffic_details[items[key_name]] += 1

                yield traffic_details, self.number
            else:
                # TODO : do we raise exception when the video ends ?
                # TODO : Handle cases when there is not vehicle (or no detection)
                print("Video has ended")

    def reset(self):
        self.video.release()
        self.out.release()


if __name__ == '__main__':
    input_data_path = "..\\static\\videos\\scenario_1"
    input_data_path = os.path.join(os.getcwd(), input_data_path)
    result = []
    with open(os.path.join(input_data_path, 'user1_inputs.json')) as cf:
        config_files = json.load(cf)
    stl_timer_default = int(config_files.get("initial_conditions").get("stl_timer_default"))

    # build lanes
    lanes = []
    lane_props_dict = config_files.get("initial_conditions").get("lane_props")
    if lane_props_dict:
        for lane_id, lane_props in lane_props_dict.items():
            if lane_props['video_feed']:
                video_path = os.path.join(input_data_path, lane_props['video_feed'])
            else:
                video_path = None
            lanes.append(Lane(int(lane_id), lane_props['status'], lane_props['lane_type']['direction'],
                              lane_props['lane_type']['exit'], video_path))
            # TODO : Build logic to support all scenarios
    else:
        print("No lanes configured by user")

    compare_lanes = [(lane, lane.get_element_count()) for lane in lanes if lane.number in [1, 2]]

    # start simulation
    sim_start_time = time.time()

    ln1_obj, ln1 = compare_lanes[0]
    ln2_obj, ln2 = compare_lanes[1]

    # initialize results dict
    results_dict = {}

    while time.time() - sim_start_time <= stl_timer_default:
        try:
            print("\033[96mTime elapsed : {:.02f}".format(time.time() - sim_start_time))
            traffic_details_1, num_1 = next(ln1)
            cnt_1 = sum(traffic_details_1.values())
            print(f"\033[91mVehicle count in lane_{num_1} is {cnt_1}")
            traffic_details_2, num_2 = next(ln2)
            cnt_2 = sum(traffic_details_2.values())
            print(f"\033[92mVehicle count in lane_{num_2} is {cnt_2}")

            # TODO : Traffic management logic goes in here
            _, lane_num = max((cnt_1, num_1), (cnt_2, num_2))

            results_dict[int(time.time() - sim_start_time)] = {f"lane_{lane_num}": True}

        except StopIteration:
            break

    ln1_obj.reset()
    ln2_obj.reset()

    print(f"results is {results_dict}")
