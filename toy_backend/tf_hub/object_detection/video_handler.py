import os
import cv2
import numpy as np
from threading import Thread

from config import CustomObject
from toy_backend import config, logger
from toy_backend.common.util import round, split_file_name, create_dir, get_date_from_file_path
from toy_backend.image.image_helper import crop_image, bound_box_image
from toy_backend.tf_hub.object_detection import ObjectDetectResult
from toy_backend.video.video_helper import video_info


class VideoHandler(object):
    def __init__(self, model_name, video_path):
        self.model_name = model_name
        self.video_path = video_path
        self.target_entities = config.object_detection.target_entities
        self.file_name = None
        self.output_dir = None
        self.json_path = None
        self.video_out = None

    def open_video(self, input_path):
        v_info = video_info(input_path)
        v_info = CustomObject(v_info)
        if v_info is not None:
            file_name, _ = split_file_name(input_path)
            output = os.path.join(self.output_dir, 'bounding-box.mp4')
            v_out = cv2.VideoWriter(filename=output,
                                    fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
                                    fps=v_info.fps,
                                    frameSize=(v_info.frame_width, v_info.frame_height))
            return v_out

    def set_out_path(self, video_path):
        # 객체 이미지 디렉토리 생성
        date = get_date_from_file_path(video_path)
        self.file_name, ext = split_file_name(video_path)
        object_detection_path = os.path.join(config.output_basedir, config.video, config.object_detection.dir_name)
        self.output_dir = os.path.join(object_detection_path, date, self.file_name, self.model_name)
        create_dir(self.output_dir)
        self.json_path = os.path.join(self.output_dir, f'{self.file_name}.json')

    def video_handler_init(self):
        if self.output_dir is None or self.video_out is None:
            print('video_handler_init')
            self.set_out_path(self.video_path)
            self.video_out = self.open_video(self.video_path)

    def write_video(self, frame):
        self.video_out.write(frame)

    def handle_detection(self, frame_cnt: int, np_image: np.ndarray, result: dict):
        if not result['detection_class_entities'][0].decode('utf-8') in self.target_entities \
                and result['detection_scores'][0] < config.object_detection.min_score:
            return None

        bounding_box_thread = Thread(target=self.bounding_box_result, args=(np_image.copy(), result))
        bounding_box_thread.start()

        return_result = self.crop_result(np_image=np_image, result=result, frame_cnt=frame_cnt)
        return return_result

    def crop_result(self, np_image, result, frame_cnt,
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
                obj_path, coordinates = crop_image(np_image, result, self.output_dir, frame_cnt)
                return_result.append(ObjectDetectResult(obj_path=obj_path,
                                                        obj=entities[i].decode('utf-8'),
                                                        score=round(scores[i], 4),
                                                        coordinates=coordinates).__dict__)
        return return_result

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

        if np_image_new is not None:
            self.write_video(np_image_new)

