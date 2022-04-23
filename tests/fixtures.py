import os.path

import numpy as np
import cv2.cv2 as cv2
import pytest

from src.defect_detector_base import DefectDetectorBase, InvalidColorMappingException
from src.defect_detector import DefectDetector
from src.defect_detector_base import InvalidInputException

current_dir = os.path.dirname(os.path.realpath(__file__))


class DefectDetectorMockup(DefectDetectorBase):
    def __init__(self):
        self.color_mapping = None

    @staticmethod
    def __check_color_mapping(mappings):
        if mappings is None:
            raise InvalidColorMappingException
        if 'knot' not in mappings:
            raise InvalidColorMappingException
        if 'crack' not in mappings:
            raise InvalidColorMappingException
        if 'stain' not in mappings:
            raise InvalidColorMappingException

    @staticmethod
    def __check_input(image: np.ndarray):
        if image is None:
            raise InvalidInputException()
        if image.ndim < 3:
            raise InvalidInputException()

    def set_color_mapping(self, mappings: dict) -> None:
        self.__check_color_mapping(mappings)
        self.color_mapping = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        self.__check_color_mapping(self.color_mapping)
        self.__check_input(image)

        result_image = cv2.imread("./data/1-defects.png")
        return cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)


@pytest.fixture()
def detector():
    return DefectDetector()


@pytest.fixture()
def grayscale_image():
    return np.zeros((442, 488))


@pytest.fixture()
def color_image():
    return np.zeros((442, 488, 3))


@pytest.fixture()
def color_mappings():
    return {
        'knot': [0, 255, 0],
        'crack': [255, 0, 0],
        'stain': [0, 0, 255]
    }


@pytest.fixture()
def test_image():
    image = cv2.imread(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "1.png"))
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


@pytest.fixture()
def test_ground_truth():
    image = cv2.imread(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "1-defects.png"))
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


@pytest.fixture()
def bbox_file():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "1.reg")
