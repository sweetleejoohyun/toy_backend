import cv2
import os
from flask import request, make_response
from datetime import date

from toy_backend import logger, config

from toy_backend.common.util import (
    create_dir,
    assign_file_name,
)
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadVideoFileRequired,
    FailedToUploadFile
)
from toy_backend.json_metadata import DetectionJson
from toy_backend.routes.route import Route
from toy_backend.tf_hub.object_detection.video_handler import VideoHandler
from toy_backend.video import (
    save_to_mp4,
    get_video_info
)


class VideoAPI(object):
    @staticmethod
    def upload_video():
        logger.debug(request)
        if 'video' not in request.files:
            raise UploadFileRequired('File not given.')
        file = request.files['video']
        if not file.filename:
            raise UploadFilenameRequired('File name not given.')
        if not file.filename.endswith(tuple(config.video_format)):
            raise UploadVideoFileRequired('Check the video file format.')

        today = date.today().strftime('%Y%m%d')
        original_dir = os.path.join(config.output_basedir, config.video, config.original_dir_name, today)
        create_dir(original_dir)

        _, extension = os.path.splitext(file.filename)
        try:
            original_path, file_name = assign_file_name(original_dir, extension)
        except RecursionError:
            raise FailedToUploadFile('Failed to assign file name.')

        # 원본 영상 저장
        path = save_to_mp4(file, original_path, file_name)

        return make_response({'path': path, 'info': get_video_info(path)}, 200)

    @staticmethod
    def run_object_detection(model, input_path):
        handler = VideoHandler(model.__class__.__name__, input_path)

        v_cap = cv2.VideoCapture(filename=input_path, apiPreference=cv2.CAP_FFMPEG)
        frame_cnt = 0
        final_result = {}
        while v_cap.isOpened():
            print(frame_cnt)
            ret, frame = v_cap.read()
            if ret:
                result = model.run_detector(frame)
                handler.video_handler_init()
                return_result = handler.handle_detection(frame_cnt, frame, result)
                if return_result:
                    final_result[frame_cnt] = return_result
            else:
                break
            frame_cnt += 1

        if final_result:
            DetectionJson.save(out_path=handler.json_path, metadata=final_result)
            return handler.json_path, final_result, handler.video_info.fps
        else:
            return None, None, None


routes = [
    Route(uri='video/upload', view_func=VideoAPI.upload_video, methods=['POST']),
]