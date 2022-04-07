import argparse
import base64

import numpy as np
import requests
import json
import os.path

import cv2.cv2 as cv2
from matplotlib import pyplot as plt


def detect_image_defects(image):
    test_image = cv2.imread(image)
    jpg = cv2.imencode('.jpg', test_image)

    base64_jpg = base64.b64encode(jpg[1])
    message = {
        'image': base64_jpg.decode('utf-8'),
        'color-mappings': {
            'knot': (255, 0, 0),
            # 'crack': (0, 255, 0),
            # 'stain': (0, 0, 255)
        }
    }

    json_message = json.dumps(message)
    header = {'Content-type': 'application/json'}

    try:
        resp = requests.post('http://127.0.0.1:8080/detect_defects', data=json_message, headers=header)
        json_resp = resp.json()

        if json_resp['result'] == 'ok':
            bytes = base64.b64decode(json_resp['data'].encode('utf-8'))
            # image = cv2.imdecode(np.frombuffer(bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            image = cv2.imdecode(np.frombuffer(bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.imshow(image)
            plt.show()
        else:
            print(f"The server returned an error")
            print(json_resp['message'])

    except requests.exceptions.ConnectionError:
        print("The server is not running. Please start the server first by running python src/server.py")

    except Exception as e:
        raise e


if __name__ == "__main__":
    def options():
        parser = argparse.ArgumentParser()

        parser.add_argument('-i', '--image',
                            help="Image to test",
                            required=True)

        return parser


    args = options().parse_args()
    image = args.image

    if not os.path.exists(image):
        raise Exception(f"La imagen de entrada {image} no existe")

    detect_image_defects(image)
