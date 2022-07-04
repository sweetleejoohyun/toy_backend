from flask import request
from datetime import date
import random

from toy_backend import logger
from toy_backend.routes.route import Route
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadImageFileRequired
)


class ImageAPI(object):
    @staticmethod
    def upload_image():
        logger.debug(request)
        if 'file' not in request.files:
            raise UploadFileRequired('File not given.')
        file = request.files['file']
        if not file.filename:
            raise UploadFilenameRequired('File name not given.')
        if not file.filename.endswith(('.jpg', '.jpeg', '.png')):
            raise UploadImageFileRequired('Check the image file format.')

        today = date.today().strftime('%Y%m%d')
        file_name = random.random()
        print(f'today : {today} / file_name : {file_name}')


routes = [
    Route(uri='image/upload', view_func=ImageAPI.upload_image, methods=['POST']),
    # Route(uri='video/<video_id>', view_func=Api.get_video),
    # Route(uri='video/<video_id>/description', view_func=Api.update_video_description, methods=['PATCH']),
    # Route(uri='video/<video_id>/groups', view_func=Api.get_objs_grouped),
    # Route(uri='videos', view_func=Api.get_videos),
    # Route(uri='videos', view_func=Api.delete_videos, methods=['DELETE'])
]