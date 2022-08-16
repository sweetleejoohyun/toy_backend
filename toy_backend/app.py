import re
import os
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import traceback

from toy_backend import logger
from toy_backend.common.exception import CustomException, FileNotFound
from toy_backend.routes import image, video
from toy_backend.tf_hub import Models, SsdMobilenetV2


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


@app.route(f'{api_root}/test')
def test():
    return jsonify('successful test!')


@app.route(f'{api_root}/image')
def send_image():
    logger.debug(request)
    try:
        return send_file(path_or_file=request.args.get('image_path'), mimetype='image/jpeg')
    except FileNotFoundError:
        return send_file(path_or_file=r'./public/images/no_image.jpg', mimetype='image/jpeg')


@app.route(f'{api_root}/video')
def send_video():
    logger.debug(request)
    try:
        full_path = request.args.get('videoPath')
        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None

        if range_header:
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])

        chunk, start, length, file_size = get_chunk(full_path, byte1, byte2)
        resp = Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)
        resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
        return resp
    except FileNotFoundError:
        raise FileNotFound('video file not found')


def get_chunk(full_path, byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.route(f'{api_root}/image/object-detection/ssdmobilenetv2', methods=['POST'])
def image_object_detection_ssdmobilenet_v2():
    logger.debug(request)
    this_model_name = 'SsdMobilenetV2'
    if not model_manager.is_exists_model(this_model_name):
        model = SsdMobilenetV2()
        model_manager.register_model(model)
    else:
        model = model_manager.get_model(this_model_name)

    json_path, final_result = image.ImageAPI.run_object_detection(model, request.json['path'])
    if final_result is None:
        return {'path': None, 'result': [{}]}
    return {'path': json_path, 'result': final_result}


@app.route(f'{api_root}/video/object-detection/ssdmobilenetv2', methods=['POST'])
def video_object_detection_ssdmobilenet_v2():
    logger.debug(request)
    this_model_name = 'SsdMobilenetV2'

    if not model_manager.is_exists_model(this_model_name):
        model = SsdMobilenetV2()
        model_manager.register_model(model)
    else:
        model = model_manager.get_model(this_model_name)

    json_path, final_result, fps = video.VideoAPI.run_object_detection(model, request.json['path'])
    if final_result is None:
        return {'path': None, 'result': [{}]}
    return {'path': json_path, 'result': final_result, 'fps': fps}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
