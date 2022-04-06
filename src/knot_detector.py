import numpy as np
import cv2.cv2 as cv2
from src.defect_detector_base import DefectDetectorBase
from tensorflow.keras import layers, Model


class KnotDetector(DefectDetectorBase):
    def __init__(self):
        super(KnotDetector, self).__init__()
        self.detectors = None
        self.color_mappings = None

    def set_color_mapping(self, mappings: dict) -> None:
        self.color_mappings = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        model: Model = self.create_model(image.shape)
        model.load_weights("../models/knot_classifier_1649238829")

        y_pred = model.predict(image[np.newaxis, ...])

        height, width, _ = image.shape

        if y_pred.shape[0] > 0:
            x, y, w, h = y_pred[0]
            x = x * width
            w = w * width
            y = y * width
            h = h * width
            # image = cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0))

        return image

    def create_model(self, input_shape: tuple):
        # create the common input layer
        input_layer = layers.Input(input_shape)

        # create the base layers
        base_layers = layers.Conv2D(16, 3, padding='same', activation='relu', name='bl_2')(input_layer)
        base_layers = layers.MaxPooling2D(name='bl_3')(base_layers)
        base_layers = layers.Conv2D(32, 3, padding='same', activation='relu', name='bl_4')(base_layers)
        base_layers = layers.MaxPooling2D(name='bl_5')(base_layers)
        base_layers = layers.Conv2D(64, 3, padding='same', activation='relu', name='bl_6')(base_layers)
        base_layers = layers.MaxPooling2D(name='bl_7')(base_layers)
        base_layers = layers.Flatten(name='bl_8')(base_layers)

        # create the localiser branch
        locator_branch = layers.Dense(128, activation='relu', name='bb_1')(base_layers)
        locator_branch = layers.Dense(64, activation='relu', name='bb_2')(locator_branch)
        locator_branch = layers.Dense(32, activation='relu', name='bb_3')(locator_branch)
        locator_branch = layers.Dense(4, activation='sigmoid', name='bb_head')(locator_branch)

        model = Model(input_layer, outputs=[locator_branch])

        return model