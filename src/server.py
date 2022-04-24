import base64
import os

import cv2.cv2 as cv2
import numpy as np
import yaml

from flask import Flask, request, json, abort, make_response, jsonify, render_template
from flask_classful import FlaskView, route

from defect_detector import DefectDetector


class RestServer(FlaskView):
    excluded_methods = ['start_server']
    route_base = '/'
    defect_detector = DefectDetector()

    def __init__(self):
        super(RestServer, self).__init__()

    @route('/detect_defects', methods=['POST'])
    def post_detect_defects(self):
        if not request.json or 'image' not in request.json:
            response = make_response(jsonify({'result': 'error', 'message': 'image is missing'}), 400)
            abort(response)

        color_mappings = request.json['color-mappings']
        bytes = base64.b64decode(request.json['image'].encode('utf-8'))
        image = cv2.imdecode(np.frombuffer(bytes, dtype=np.uint8), 1)

        try:
            self.defect_detector.set_color_mapping(color_mappings)
            result = self.defect_detector.detect_defects(image)

            result = cv2.imencode('.jpg', result)
            result = base64.b64encode(result[1]).decode('utf-8')
            return make_response(jsonify({'result': 'ok', 'data': result}), 200)
        except Exception as e:
            response = make_response(
                jsonify({'result': 'error', 'message': f"The defect detector returned and error: {e.message}"}), 500)
            abort(response)

        abort(make_response({
            'result': 'error',
            'message': 'Unknown error, please contact service provider.'
        }), 500)

    @route('/', methods=['GET'])
    def get_root(self):
        resp = make_response(render_template('index.html'), 200)
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        return resp


def get_server_config():
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found.")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    server_config = config['SERVER']
    return server_config


if __name__ == '__main__':
    server_config = get_server_config()
    app = Flask(__name__, static_folder='html/static', template_folder='html/templates')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    RestServer.register(app)
    app.run(host=server_config['HOST'], port=server_config['PORT'])
