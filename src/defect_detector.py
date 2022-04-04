import numpy as np

from .crack_detector import CrackDetector
from .defect_detector_base import DefectDetectorBase, InvalidColorMappingException, InvalidInputException
from .knot_detector import KnotDetector
from .stain_detector import StainDetector


class DefectDetector(DefectDetectorBase):
    def __init__(self):
        super(DefectDetector, self).__init__()

        self.detectors = {
            'knot': KnotDetector(),
            'crack': CrackDetector(),
            'stain': StainDetector()
        }

        self.color_mappings: dict = None

    def set_color_mapping(self, mappings: dict) -> None:
        if mappings is None or not np.all(list(sorted(mappings.keys())) == list(sorted(self.detectors.keys()))):
            raise InvalidColorMappingException()
        self.color_mappings = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        if self.color_mappings is None or not np.all(
                list(sorted(self.color_mappings.keys())) == list(sorted(self.detectors.keys()))):
            raise InvalidColorMappingException()

        if image is None or image.ndim != 3:
            raise InvalidInputException()

        result = np.zeros(image.shape)

        for name, detector in self.detectors.items():
            detector.set_color_mapping({name: self.color_mappings[name]})
            result += detector.detect_defects(image)

        return result
