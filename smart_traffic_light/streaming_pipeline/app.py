from flask import Response
from flask import Flask, render_template
from consumer import get_video_stream
import requests


app = Flask(__name__)


@app.route('/video', methods=['GET'])
def video():
    return Response(
        get_video_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
