from flask import request
from datetime import date
import random

from toy_backend import logger
from toy_backend.routes.route import Route
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadVideoFileRequired
)


class VideoAPI(object):
    @staticmethod
    def upload_video():
        logger.debug(request)
        if 'file' not in request.files:
            raise UploadFileRequired('File not given.')
        file = request.files['file']
        if not file.filename:
            raise UploadFilenameRequired('File name not given.')
        if not file.filename.endswith(('.mp4', '.avi', '.av1')):
            raise UploadVideoFileRequired('Check the video file format.')

        today = date.today().strftime('%Y%m%d')
        file_name = random.random()
        print(f'today : {today} / file_name : {file_name}')


routes = [
    Route(uri='video/upload', view_func=VideoAPI.upload_video, methods=['POST']),
]