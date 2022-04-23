import os
import glob
import importlib
import re

import numpy as np

from defect_detector_base import DefectDetectorBase, InvalidColorMappingException, InvalidInputException


class DefectDetector(DefectDetectorBase):
    def __init__(self):
        super(DefectDetector, self).__init__()
        self.detectors = self.__load_detectors()
        self.color_mappings: dict = None

    def __load_detectors(self):
        detectors = {}
        detector_name_regex = "(.*)_detector.py"

        for detector_file in glob.glob(os.path.join(self.detectors_folder, "*_detector.py")):
            basename = os.path.basename(detector_file)
            name_search = re.search(detector_name_regex, basename)
            groups = name_search.groups()

            if len(groups) > 0:
                module_name = groups[0]
                class_name = f"{module_name.title()}Detector"
                detector_module = importlib.import_module(f"detectors.{os.path.splitext(basename)[0]}")
                detector_class = getattr(detector_module, class_name)
                detectors[module_name] = detector_class()

        return detectors

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
