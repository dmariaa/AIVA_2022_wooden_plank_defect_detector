from fixtures import *


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
