import os
from flask import request, make_response
from datetime import date


from toy_backend import logger, config
from toy_backend.image.image_helper import to_ndarray
from toy_backend.json_metadata import DetectionJson
from toy_backend.routes.route import Route
from toy_backend.common.util import (
    create_dir,
    assign_file_name,
)
from toy_backend.image import (
    save_to_jpg,
    get_image_info
)
from toy_backend.common.exception import (
    UploadFileRequired,
    UploadFilenameRequired,
    UploadImageFileRequired,
    FailedToUploadFile
)
from toy_backend.tf_hub.object_detection.image_handler import ImageHandler


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
        path = save_to_jpg(file, original_path, file_name)

        return make_response({'path': path, 'info': get_image_info(path)}, 200)

    @staticmethod
    def run_object_detection(model, input_path):
        handler = ImageHandler(model.__class__.__name__, input_path)

        # convert to ndarray
        np_image = to_ndarray(input_path)
        # run detection
        result = model.run_detector(np_image)
        # handle result
        final_result = handler.handle_detection(np_image, result)

        if final_result:
            DetectionJson.save(out_path=handler.json_path, metadata=final_result)
            return handler.json_path, final_result
        else:
            return None, None


routes = [
    Route(uri='image/upload', view_func=ImageAPI.upload_image, methods=['POST']),
]