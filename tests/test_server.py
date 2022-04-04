import base64
import http.client
import json

from fixtures import *


def test_detect(test_image: np.ndarray, test_ground_truth: np.ndarray):
    jpg = cv2.imencode('.jpg', test_image)
    base64_jpg = base64.b64encode(jpg)
    message = {'image': base64_jpg}
    json_message = json.dumps(message)

    header = {'Content-type': 'application/json'}
    conn = http.client.HTTPConnection(host='127.0.0.1', port=8080)
    conn.request('POST', '/detect-defects', json_message, header)

    resp = conn.getresponse()
