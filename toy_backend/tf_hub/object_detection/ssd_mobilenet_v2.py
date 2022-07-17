# model name : openimages_v4/ssd/mobilenet_v2
# https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1
import tensorflow_hub as tf_hub

from toy_backend.image.object_detection import ObjectDetection


class SsdMobilenetV2(ObjectDetection):
    def __init__(self):
        super(SsdMobilenetV2, self).__init__()

    def load_model(self):
        if self.model is None:
            module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
            self.model = tf_hub.load(module_handle).signatures['default']
