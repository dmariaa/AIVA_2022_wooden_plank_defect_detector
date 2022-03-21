import pytest
import numpy as np
import cv2.cv2 as cv2

from src.defect_detector_base import DefectDetectorBase, InvalidColorMappingException, InvalidInputException


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
    return DefectDetectorMockup()


@pytest.fixture()
def grayscale_image():
    return np.zeros((488, 442))


@pytest.fixture()
def color_image():
    return np.zeros((488, 442, 3))


@pytest.fixture()
def color_mappings():
    return {
        'knot': [0, 255, 0],
        'crack': [255, 0, 0],
        'stain': [0, 0, 255]
    }


@pytest.fixture()
def test_image():
    image = cv2.imread("./data/1.png")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


@pytest.fixture()
def test_ground_truth():
    image = cv2.imread("./data/1-defects.png")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def test_no_color_mapping_exception(detector: DefectDetectorBase):
    with pytest.raises(InvalidColorMappingException):
        detector.detect_defects(None)


def test_incomplete_color_mapping_exception(detector: DefectDetectorBase):
    with pytest.raises(InvalidColorMappingException):
        detector.set_color_mapping({
            'knot': [0, 255, 0],
            'crack': [255, 0, 0]
        })


def test_no_image_exception(detector: DefectDetectorBase, color_mappings: dict):
    detector.set_color_mapping(color_mappings)

    with pytest.raises(InvalidInputException):
        detector.detect_defects(None)


def test_invalid_image_exception(detector: DefectDetectorBase, grayscale_image: np.ndarray, color_mappings: dict):
    detector.set_color_mapping(color_mappings)

    with pytest.raises(InvalidInputException):
        detector.detect_defects(grayscale_image)


def test_returned_image_format(detector: DefectDetectorBase, color_image: np.ndarray, color_mappings: dict):
    detector.set_color_mapping(color_mappings)
    result = detector.detect_defects(color_image)

    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.ndim == 3


def test_detection(detector: DefectDetectorBase, test_image: np.ndarray, test_ground_truth: np.ndarray,
                   color_mappings: dict):
    detector.set_color_mapping(color_mappings)
    result = detector.detect_defects(test_image)
    assert np.all(result == test_ground_truth)
