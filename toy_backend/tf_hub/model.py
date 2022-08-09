import time
import numpy as np
import tensorflow as tf

from toy_backend import config, logger


class Models(object):
    def __init__(self):
        self.models = {}

    def register_model(self, model):
        self.models[model.__class__.__name__] = model
        logger.info(f'models : {self.models}')

    def is_exists_model(self, model_name):
        if model_name in self.models:
            return True
        else:
            return False

    def get_model(self, model_name):
        logger.info(f'models : {self.models}')
        return self.models.get(model_name)

    def delete_model(self, model_name):
        self.models.pop(model_name)


class LoadedModel(object):
    def __init__(self):
        self.model = None
        self.model_name = self.__class__.__name__
        self.load_model()

    def load_model(self):
        logger.info(f'{self.model_name} - loaded model!')


class ObjectDetectionModel(LoadedModel):
    def __init__(self):
        super(ObjectDetectionModel, self).__init__()

    # run object detection
    def run_detector(self, np_image: np.ndarray):
        # change BGR to RGB
        np_image = np_image[:, :, ::-1]
        # convert nd_array to tensor
        tensor_img = tf.convert_to_tensor(np_image, dtype=tf.uint8)
        # convert to dtype(uint8->float32)
        tensor_img = tf.image.convert_image_dtype(tensor_img, tf.float32)[tf.newaxis, ...]

        start_time = time.time()
        if config.use_gpu:
            result = self.model(tensor_img)
        else:
            with tf.device('/CPU:0'):
                result = self.model(tensor_img)
        end_time = time.time()

        # convert tensor to ndarray
        result = {key: value.numpy() for key, value in result.items()}
        logger.debug("Found %d objects." % len(result["detection_class_entities"]))
        logger.debug(f"detected time : {end_time - start_time:.5f} sec")
        return result