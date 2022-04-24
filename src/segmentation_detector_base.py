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


class SegmentationDetectorBase(DefectDetectorBase):
    MODEL_DRIVE_ID = None
    DEFECT_TYPE = None
    MODEL_LOCAL_NAME = None

    def __init__(self):
        super(SegmentationDetectorBase, self).__init__()

        if self.MODEL_DRIVE_ID is None:
            raise NotImplementedError(f"MODEL_DRIVE_ID is None, probable you should inherit this class")

        self.detectors = None
        self.color_mappings = None
        self.__load_model()

    def __load_model(self):
        self.model_file = os.path.join(self.models_folder, self.MODEL_LOCAL_NAME)
        google_drive_download(self.MODEL_DRIVE_ID, self.model_file)
        self.model = tf.keras.models.load_model(self.model_file)

    def _normalize_image(self, image):
        image = image.copy() / 255.
        image = np.pad(image, ((3, 3), (4, 4), (0, 0)))
        return image

    def set_color_mapping(self, mappings: dict) -> None:
        self.color_mappings = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        color = self.color_mappings[self.DEFECT_TYPE]
        predict_image = self._normalize_image(image)
        y_pred = self.model.predict(predict_image[np.newaxis, ...])

        # Resize, threshold and binarize
        y_pred = y_pred[0, 3:-3, 4:-4, :]
        y_pred.copy().reshape(y_pred.shape[:-1])
        y_pred[y_pred >= 0.5] = 1.0
        y_pred[y_pred < 0.5] = 0.0

        # apply_color_mapping
        y_pred_color = cv2.cvtColor(y_pred, cv2.COLOR_GRAY2RGB)
        y_pred_color *= color

        return y_pred_color
