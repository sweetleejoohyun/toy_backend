import os
from flask import request, make_response
from datetime import date
import random

from toy_backend import logger, config
from toy_backend.routes.route import Route
from toy_backend.common.util import (
    create_dir,
    assign_file_name,
)
from toy_backend.video import (
    save_to_mp4
)
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadVideoFileRequired,
    FailedToUploadFile
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
        save_to_mp4(file, original_path, file_name)

        # 객체 이미지 디렉토리 생성
        obj_detection_path = os.path.join(config.output_basedir, config.video, config.object_detection_dir_name, today)
        create_dir(obj_detection_path)
        return make_response({'message': 'Video is uploaded successfully'}, 200)


routes = [
    Route(uri='video/upload', view_func=VideoAPI.upload_video, methods=['POST']),
]