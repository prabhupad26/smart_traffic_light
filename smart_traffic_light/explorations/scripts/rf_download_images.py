import os

HOME = os.getcwd()
HOME = os.path.join(HOME, "..\\..\\raw_data")
os.environ['HOME'] = HOME
os.chdir(os.path.join(HOME, 'datasets'))

from roboflow import Roboflow

rf = Roboflow(api_key="HDll2oFm5X8KK35ziZJL")
project = rf.workspace("casestudy1").project("smart-traffic-light")
dataset = project.version(26).download("yolov8")
