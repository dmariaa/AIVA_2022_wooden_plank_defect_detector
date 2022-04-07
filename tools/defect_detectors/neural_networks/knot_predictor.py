import glob
import os

import cv2
import numpy as np
import tensorflow as tf

from src.image_tools import image_file_sorter
from tools.defect_detectors.neural_networks.knot_classifier import load_pickle_file


def paint_bounding_boxes(image, bboxes, **kwargs):
    output_image = image.copy()

    for x, y, w, h in bboxes.astype(int):
        output_image = cv2.rectangle(img=output_image, pt1=(x, y), pt2=(x + w, y + h), **kwargs)

    return output_image


def predictions_test(data: str, model: str, out: str):
    if os.path.isfile(data):
        images, bboxes = load_pickle_file(data)
    else:
        image_files = sorted(glob.glob(os.path.join(data, "*.png")), key=image_file_sorter)
        images = []

        for image_file in image_files:
            image = cv2.imread(image_file)
            images.append(image)

        images = np.array(images)

    model = tf.keras.models.load_model(model)

    for i, image in enumerate(images):
        predict_image = image.copy() / 255.
        y_pred = model.predict(predict_image[np.newaxis, ...])

        x, y, w, h = y_pred[0]
        image_height, image_width, _ = image.shape

        x = x * image_width
        w = w * image_width
        y = y * image_height
        h = h * image_height

        image = paint_bounding_boxes(image, np.array([[x, y, w, h]]).astype(int), color=(0, 255, 0))
        file_name = os.path.basename(image_files[i])
        cv2.imwrite(os.path.join(out, file_name), image)


if __name__ == "__main__":
    import argparse


    def options():
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--data",
                            help="Dataset folder or pickle file",
                            required=True,
                            type=str)

        parser.add_argument("-m", "--model",
                            help="Path to save trained model weights",
                            required=True,
                            type=str)

        parser.add_argument("-o", "--output",
                            help="Path to save tested images",
                            required=True,
                            type=str)

        return parser


    args = options().parse_args()
    data = args.data
    output_folder = args.output
    model = args.model

    predictions_test(data=data, model=model, out=output_folder)
