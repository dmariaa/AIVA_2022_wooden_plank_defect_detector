import base64
import cv2.cv2 as cv2
import numpy as np

from flask import Flask, request, json, abort, make_response, jsonify
from flask_classful import FlaskView, route

from defect_detector import DefectDetector


class RestServer(FlaskView):
    excluded_methods = ['run']
    route_base = '/'

    def __init__(self):
        super(RestServer, self).__init__()
        self.defect_detector = DefectDetector()

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
        return 'OK'

    def start_server(self):
        app.run(host='0.0.0.0', port=8080)


app = Flask(__name__)
RestServer.register(app)

if __name__ == '__main__':
    server = RestServer()
    server.start_server()
