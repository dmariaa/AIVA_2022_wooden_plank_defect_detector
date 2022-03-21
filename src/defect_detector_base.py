import numpy as np


class DefectDetectorBase:
    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        raise Exception("Not implemented")

    def set_color_mapping(self, mappings: dict) -> None:
        raise Exception("Not implemented")


class DefectDetectorException(Exception):
    pass


class InvalidInputException(DefectDetectorException):
    def __init__(self):
        self.message = "Invalid input"


class UncertainResultException(DefectDetectorException):
    def __init__(self):
        self.message = "The result of detection is uncertain"


class InvalidColorMappingException(DefectDetectorException):
    def __init__(self):
        self.message = "Invalid color mapping"
