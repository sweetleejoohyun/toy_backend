import os
import time
import cv2
import numpy as np
import tensorflow as tf
from threading import Thread

from config import CustomObject
from toy_backend import config, logger
from toy_backend.common.util import create_dir, split_file_name, get_date_from_file_path, is_file_exist
from toy_backend.image.image_helper import crop_image, segment_image
from toy_backend.json_metadata import DetectionJson


class ObjectDetectResult(CustomObject):
    def __init__(self, obj_path, obj, score, coordinates):
        super(ObjectDetectResult, self).__init__()
        self.obj_path = obj_path
        self.obj = obj
        self.score = score
        self.coordinates = coordinates


class ObjectDetection(object):
    def __init__(self):
        self.model = None
        self.target_entities = config.object_detection.target_entities
        self.load_model()

    def load_model(self):
        pass

    def set_out_path(self, input_path):
        # 객체 이미지 디렉토리 생성
        date = get_date_from_file_path(input_path)
        file_name, ext = split_file_name(input_path)
        model_name = self.__class__.__name__
        object_detection_path = os.path.join(config.output_basedir, config.image, config.object_detection.dir_name)
        self.output_dir = os.path.join(object_detection_path, date, file_name, model_name)
        create_dir(self.output_dir)

    # run object detection
    def run_detector(self, image_path):
        if not is_file_exist(image_path):
            return None, None

        self.set_out_path(image_path)
        np_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # change BGR to RGB
        np_image = np_image[:,:,::-1]
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

        # result is sorted by score
        result = {key: value.numpy() for key, value in result.items()}
        logger.debug("Found %d objects." % len(result["detection_scores"]))
        logger.debug(f"detected time : {end_time - start_time:.5f} sec")

        np_image = np_image[:,:,::-1]
        segment_thread = Thread(target=self.segmentation_result, args=(np_image.copy(), result))
        segment_thread.start()

        final_result = self.crop_result(np_image=np_image, result=result)
        json_path = os.path.join(self.output_dir, '0.json')
        DetectionJson.save(out_path=json_path, metadata=final_result)
        return json_path, final_result

    def crop_result(self, np_image, result,
                    return_cnt=config.object_detection.return_cnt,
                    min_score=config.object_detection.min_score):
        final_result = []
        boxes = result['detection_boxes']
        entities = result['detection_class_entities']
        scores = result['detection_scores']

        for i in range(min(entities.shape[0], return_cnt)):
            if entities[i].decode('utf-8') in self.target_entities and scores[i] >= min_score:
                result = (boxes[i], entities[i].decode('utf-8'), scores[i])
                # save crop helper
                obj_path, coordinates = crop_image(np_image, result, self.output_dir)
                final_result.append(ObjectDetectResult(obj_path=obj_path,
                                                       obj=entities[i].decode('utf-8'),
                                                       score=scores[i].item(),
                                                       coordinates=coordinates).__dict__)
        if len(final_result) == 0:
            return None
        else:
            return final_result

    def segmentation_result(self, np_image, result,
                            return_cnt=config.object_detection.return_cnt,
                            min_score=config.object_detection.min_score):
        np_image_new = np.empty(shape=(0, 0))
        boxes = result['detection_boxes']
        entities = result['detection_class_entities']
        scores = result['detection_scores']

        for i in range(min(entities.shape[0], return_cnt)):
            if entities[i].decode('utf-8') in self.target_entities and scores[i] >= min_score:
                result = (boxes[i], entities[i].decode('utf-8'), scores[i])
                np_image_new = segment_image(np_image, result)

        if np_image_new.size == 0:
            pass
        else:
            seg_output_path = os.path.join(self.output_dir, 'segmentation.jpg')
            cv2.imwrite(seg_output_path, np_image_new)
