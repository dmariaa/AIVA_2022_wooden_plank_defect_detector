import numpy as np

from src.defect_detector_base import DefectDetectorBase


class CrackDetector(DefectDetectorBase):
    def __init__(self):
        super(CrackDetector, self).__init__()
        self.detectors = None
        self.color_mappings = None

    def set_color_mapping(self, mappings: dict) -> None:
        self.color_mappings = mappings

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        return np.zeros(image.shape)
