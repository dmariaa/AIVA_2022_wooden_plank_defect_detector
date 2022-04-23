import os
import yaml

import numpy as np


class DefectDetectorBase:
    def __init__(self):
        self.current_folder = os.path.dirname(os.path.realpath(__file__))
        self.config = self.__read_config()

    def __read_config(self):
        config_file = os.path.join(self.current_folder, 'config.yaml')
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file {config_file} not found.")

        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def detect_defects(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError()

    def set_color_mapping(self, mappings: dict) -> None:
        raise NotImplementedError()


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
