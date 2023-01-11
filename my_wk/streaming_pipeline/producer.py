from kafka import KafkaProducer
import cv2
import sys


class PublishVideoData:
    def __init__(self, file_name, producer_obj, kafka_topic):
        self.file_name = file_name
        self.producer_obj = producer_obj
        self.kafka_topic = kafka_topic

    def publish_data(self):
        video = cv2.VideoCapture(self.file_name)
        while video.isOpened():
            success, frame = video.read()

            # Ensure file was read successfully
            if not success:
                print("bad read!")
                break

            # Convert image to png
            ret, buffer = cv2.imencode('.jpg', cv2.resize(frame, (640, 640)))

            # Convert to bytes and send to kafka
            self.producer_obj.send(self.kafka_topic, buffer.tobytes())
            print(f"Sent video feed {sys.getsizeof(buffer.tobytes())} bytes ------> {self.kafka_topic}")

            # time.sleep(0.2)
        video.release()
        print("Publish Success")


if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092']
    )
    publish_lane_1 = PublishVideoData("lane_1_feed.mp4", producer, "videotest")
    publish_lane_2 = PublishVideoData("lane_2_feed.mp4", producer, "videotest")
    publish_lane_1.publish_data()
