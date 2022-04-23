import os
import os.path

from tools.download_tools import onedrive_download, google_drive_download

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import cv2.cv2 as cv2
from src.defect_detector_base import DefectDetectorBase

import tensorflow as tf
from tensorflow.keras import layers, Model

tf.get_logger().setLevel('ERROR')
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


class KnotDetector(DefectDetectorBase):
    MODEL_URL = "https://drive.google.com/uc?id=1leux1CMUnWyWtVcIaJ7kyMKs3c8WvA3K"

    def __init__(self):
        super(KnotDetector, self).__init__()
        self.detectors = None
        self.color_mappings = None
        self.__load_model()

    def __load_model(self):
        self.model_file = os.path.join(self.models_folder, "knot-detector-model.h5")
        google_drive_download(KnotDetector.MODEL_URL, self.model_file)
        self.model = tf.keras.models.load_model(self.model_file)

    def set_color_mapping(self, mappings: dict) -> None:
        self.color_mappings = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        # model: Model = self.create_model(image.shape)
        # model.load_weights("../models/knot_classifier_1649238829")

        predict_image = image.copy() / 255.
        y_pred = self.model.predict(predict_image[np.newaxis, ...])

        height, width, _ = image.shape

        if y_pred.shape[0] > 0:
            x, y, w, h = y_pred[0]
            x = int(x * width)
            w = int(w * width)
            y = int(y * height)
            h = int(h * height)
            image = cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0))

        return image