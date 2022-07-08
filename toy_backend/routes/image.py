import os
from flask import request, make_response
from datetime import date


from toy_backend import logger, config
from toy_backend.routes.route import Route
from toy_backend.common.util import (
    create_dir,
    assign_file_name,
    save_to_jpg
)
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadImageFileRequired,
    FailedToUploadFile
)


class ImageAPI(object):
    @staticmethod
    def upload_image():
        logger.debug(request)
        if 'image' not in request.files:
            raise UploadFileRequired('File not given.')
        file = request.files['image']
        if not file.filename:
            raise UploadFilenameRequired('File name not given.')
        if not file.filename.endswith(tuple(config.image_format)):
            raise UploadImageFileRequired('Check the image file format.')

        today = date.today().strftime('%Y%m%d')
        original_dir = os.path.join(config.output_basedir, config.image, config.original_dir_name, today)
        create_dir(original_dir)

        _, extension = os.path.splitext(file.filename)
        try:
            original_path, file_name = assign_file_name(original_dir, extension)
        except RecursionError:
            raise FailedToUploadFile('Failed to assign file name.')

        # 원본 이미지 저장
        save_to_jpg(file, original_path, file_name)

        # 객체 이미지 디렉토리 생성
        obj_detection_path = os.path.join(config.output_basedir, config.image, config.object_detection_dir_name, today)
        create_dir(obj_detection_path)
        return make_response({'message': 'Image is uploaded successfully'}, 200)


routes = [
    Route(uri='image/upload', view_func=ImageAPI.upload_image, methods=['POST']),
]