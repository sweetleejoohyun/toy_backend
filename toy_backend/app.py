from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import traceback

from toy_backend import logger, config
from routes import image, video
from common.exception import CustomException

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
api_root = '/api'
routes = image.routes + video.routes
[app.add_url_rule(rule=f'{api_root}/{r.uri}', view_func=r.view_func, methods=r.methods) for r in routes]


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
