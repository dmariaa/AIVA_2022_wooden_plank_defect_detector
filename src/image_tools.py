import os.path

import cv2.cv2 as cv2


def get_bounding_boxes(bbox_file):
    assert os.path.exists(bbox_file), f"The file {bbox_file} does not exists"
    f = cv2.FileStorage()

    f.open(bbox_file, cv2.FILE_STORAGE_READ)
    gt_data = f.getNode('rectangles').mat()

    rects = []

    for rect_idx in range(0, gt_data.shape[1]):
        x, y, width, height = gt_data[:, rect_idx]
        rects.append((x, y, width, height))

    return rects


def paint_bounding_boxes(image, bboxes, **kwargs):
    output_image = image.copy()

    for x1, y1, x2, y2 in bboxes.astype(int):
        output_image = cv2.rectangle(img=output_image, pt1=(x1, y1), pt2=(x2, y2), **kwargs)

    return output_image


def image_file_sorter(file):
    dir = os.path.dirname(file)
    f, ext = os.path.splitext(os.path.basename(file))
    return f"{dir}{int(f):05d}"
