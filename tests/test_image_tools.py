import pytest
from fixtures import *

from src.image_tools import get_bounding_boxes


def test_get_bounding_boxes(bbox_file):
    rects = get_bounding_boxes(bbox_file)
    assert len(rects) == 2
    assert (39, 231, 22, 29) in rects
    assert (393, 273, 27, 35) in rects
