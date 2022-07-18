from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import traceback

from toy_backend import logger
from toy_backend.json_metadata import DetectionJson
from toy_backend.routes import image, video
from toy_backend.common.exception import CustomException
from toy_backend.tf_hub import Models, SsdMobilenetV2
from toy_backend.image.image_helper import to_ndarray
from toy_backend.tf_hub.object_detection.image_handler import ImageHandler
from toy_backend.tf_hub.object_detection.video_handler import VideoHandler

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
api_root = '/api'
routes = image.routes + video.routes
[app.add_url_rule(rule=f'{api_root}/{r.uri}', view_func=r.view_func, methods=r.methods) for r in routes]

# model manager
model_manager = Models()


@app.errorhandler(CustomException)
def handle_error(e):
    traceback.print_exc()
    return jsonify(e.to_dict(), e.status_code)


@app.route(f'{api_root}/image')
def send_image():
    logger.debug(request)
    try:
        return send_file(path_or_file=request.args.get('image_path'), mimetype='image/jpeg')
    except FileNotFoundError:
        return send_file(path_or_file=r'D:\React\toy-front\public\images\no_image.jpg', mimetype='image/jpeg')


@app.route(f'{api_root}/image/object-detection/ssdmobilenetv2', methods=['POST'])
def image_object_detection_ssdmobilenet_v2():
    logger.debug(request)
    this_model_name = 'SsdMobilenetV2'
    handler = ImageHandler(this_model_name, request.json['path'])
    if not model_manager.is_exists_model(this_model_name):
        model = SsdMobilenetV2()
        model_manager.register_model(model)
    else:
        model = model_manager.get_model(this_model_name)

    # convert to ndarray
    np_image = to_ndarray(request.json['path'])
    # run detection
    result = model.run_detector(np_image)
    # handle result
    final_result = handler.handle_detection(np_image, result)

    if final_result is None:
        return {'path': None, 'result': [{}]}

    print({'path': handler.json_path, 'result': final_result})
    return {'path': handler.json_path, 'result': final_result}


import cv2
@app.route(f'{api_root}/video/object-detection/ssdmobilenetv2', methods=['POST'])
def video_object_detection_ssdmobilenet_v2():
    logger.debug(request)
    this_model_name = 'SsdMobilenetV2'
    handler = VideoHandler(this_model_name, request.json['path'])
    if not model_manager.is_exists_model(this_model_name):
        model = SsdMobilenetV2()
        model_manager.register_model(model)
    else:
        model = model_manager.get_model(this_model_name)

    v_cap = cv2.VideoCapture(filename=request.json['path'], apiPreference=cv2.CAP_FFMPEG)
    frame_cnt = 0
    final_result = {}
    while v_cap.isOpened() and frame_cnt < 20:
        ret, frame = v_cap.read()
        if ret:
            result = model.run_detector(frame)
            handler.video_handler_init()
            return_result = handler.handle_detection(frame_cnt, frame, result)
            if return_result is not None:
                final_result[frame_cnt] = return_result
            frame_cnt += 1

    print(final_result)
    DetectionJson.save(out_path=handler.json_path, metadata=final_result)
    return {'path': handler.json_path, 'result': [{}]}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
