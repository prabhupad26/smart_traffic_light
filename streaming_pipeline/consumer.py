from flask import Flask, Response
from kafka import KafkaConsumer
import requests

topic = "videotest"

consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'])


app = Flask(__name__)


@app.route('/video', methods=['GET'])
def video():
    return Response(
        get_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


def get_video_stream():
    for msg in consumer:
        # response_json = requests.post('http://127.0.0.1:5000/v1/object-detection/v1_model',
        #                               data=msg.value,
        #                               headers={'Content-Type': 'application/octet-stream'})
        # TODO : Add bbox details to the image byte stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpg\r\n\r\n' + msg.value + b'\r\n\r\n')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
