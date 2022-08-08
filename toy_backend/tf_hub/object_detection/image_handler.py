import os
import cv2
import numpy as np
from threading import Thread

from toy_backend import config, logger
from toy_backend.common.util import round, split_file_name, create_dir, get_date_from_file_path
from toy_backend.image.image_helper import crop_image, bound_box_image
from toy_backend.json_metadata import DetectionJson
from toy_backend.tf_hub.object_detection import ObjectDetectResult


class ImageHandler(object):
    def __init__(self, model_name, image_path):
        self.model_name = model_name
        self.image_path = image_path
        self.target_entities = config.object_detection.target_entities
        self.file_name = None
        self.output_dir = None
        self.json_path = None

    def set_out_path(self, image_path):
        # 객체 이미지 디렉토리 생성
        date = get_date_from_file_path(image_path)
        self.file_name, _ = split_file_name(image_path)
        object_detection_path = os.path.join(config.output_basedir, config.image, config.object_detection.dir_name)
        self.output_dir = os.path.join(object_detection_path, date, self.file_name, self.model_name)
        create_dir(self.output_dir)
        self.json_path = os.path.join(self.output_dir, f'{self.file_name}.json')

    def handle_detection(self, np_image: np.ndarray, result: dict):
        if not result['detection_class_entities'][0].decode('utf-8') in self.target_entities and \
                result['detection_scores'][0] < config.object_detection.min_score:
            return None

        self.set_out_path(self.image_path)
        bounding_box_thread = Thread(target=self.bounding_box_result, args=(np_image.copy(), result))
        bounding_box_thread.start()

        return_result = self.crop_result(np_image=np_image, result=result)
        if return_result is None:
            return None
        else:
            final_result = {'0': return_result}
            # DetectionJson.save(out_path=self.json_path, metadata=final_result)
            return final_result

    def crop_result(self, np_image, result,
                    return_cnt=config.object_detection.return_cnt,
                    min_score=config.object_detection.min_score):
        return_result = []
        boxes = result['detection_boxes']
        entities = result['detection_class_entities']
        scores = result['detection_scores']

        for i in range(min(entities.shape[0], return_cnt)):
            if entities[i].decode('utf-8') in self.target_entities and scores[i] >= min_score:
                result = (boxes[i], entities[i].decode('utf-8'), round(scores[i], 4))
                # save crop helper
                obj_path, coordinates = crop_image(np_image, result, self.output_dir)
                return_result.append(ObjectDetectResult(obj_path=obj_path,
                                                        obj=entities[i].decode('utf-8'),
                                                        score=round(scores[i], 4),
                                                        coordinates=coordinates).__dict__)
        if return_result:
            return return_result
        else:
            return None


    def bounding_box_result(self, np_image, result,
                            return_cnt=config.object_detection.return_cnt,
                            min_score=config.object_detection.min_score):
        np_image_new = np.empty(shape=(0, 0))
        boxes = result['detection_boxes']
        entities = result['detection_class_entities']
        scores = result['detection_scores']

        for i in range(min(entities.shape[0], return_cnt)):
            if entities[i].decode('utf-8') in self.target_entities and scores[i] >= min_score:
                result = (boxes[i], entities[i].decode('utf-8'), round(scores[i], 4))
                np_image_new = bound_box_image(np_image, result)

        if np_image_new.size == 0:
            pass
        else:
            seg_output_path = os.path.join(self.output_dir, 'bounding-box.jpg')
            cv2.imwrite(seg_output_path, np_image_new)