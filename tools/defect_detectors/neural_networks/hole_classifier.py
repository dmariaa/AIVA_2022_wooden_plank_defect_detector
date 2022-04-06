import glob
import os.path
import pickle
import time

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from sklearn.model_selection import train_test_split

from src.image_tools import image_file_sorter


def create_model(input_shape: tuple):
    # create the common input layer
    input_layer = layers.Input(input_shape)

    # create the base layers
    base_layers = layers.Conv2D(16, 3, padding='same', activation='relu', name='bl_2')(input_layer)
    base_layers = layers.MaxPooling2D(name='bl_3')(base_layers)
    base_layers = layers.Conv2D(32, 3, padding='same', activation='relu', name='bl_4')(base_layers)
    base_layers = layers.MaxPooling2D(name='bl_5')(base_layers)
    base_layers = layers.Conv2D(64, 3, padding='same', activation='relu', name='bl_6')(base_layers)
    base_layers = layers.MaxPooling2D(name='bl_7')(base_layers)
    base_layers = layers.Flatten(name='bl_8')(base_layers)

    # create the localiser branch
    locator_branch = layers.Dense(128, activation='relu', name='bb_1')(base_layers)
    locator_branch = layers.Dense(64, activation='relu', name='bb_2')(locator_branch)
    locator_branch = layers.Dense(32, activation='relu', name='bb_3')(locator_branch)
    locator_branch = layers.Dense(4, activation='sigmoid', name='bb_head')(locator_branch)

    model = Model(input_layer, outputs=[locator_branch])

    return model


def prepare_data(images: list, bboxes: list):
    # image is in BGR format, normalize to 0.-1.
    images = np.array(images)
    images = images / 255.

    # extract bboxes
    single_bboxes = np.zeros((images.shape[0], 4))
    for i, bbox in enumerate(bboxes):
        if bbox.shape[0] > 0:
            b = bbox[0]

            image = images[i]
            image_height, image_width, _ = image.shape

            # transform (x1, y1, x2, y2) to (x, y, w, h)
            b[2] = b[2] - b[0]
            b[3] = b[3] - b[0]

            # normalize b to 0-1 range
            b[0] = b[0] / image_width
            b[2] = b[2] / image_width
            b[1] = b[1] / image_height
            b[3] = b[3] / image_height

            single_bboxes[i] = b

    X_train, X_val, Y_train, Y_val = train_test_split(images, single_bboxes, test_size=0.2, random_state=8)
    return X_train, X_val, Y_train, Y_val


def load_pickle_file(pickle_file):
    with open(pickle_file, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
        pickle_file.close()

    images = data['images']
    image_bounding_boxes = data['bboxes']
    bboxes = []

    for ibboxes in image_bounding_boxes:
        bboxes.append(ibboxes.to_xyxy_array())

    return images, bboxes


def train(data: str, output: str, lr: float = 1e-4, batch_size: int = 5, epochs: int = 100):
    if os.path.isfile(data):
        images, bboxes = load_pickle_file(data)

    X_train, X_val, Y_train, Y_val = prepare_data(images, bboxes)

    model = create_model(X_train.shape[1:])
    loss = tf.keras.losses.MSE
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])

    model.fit(X_train, Y_train,
              validation_data=(X_val, Y_val),
              batch_size=batch_size,
              epochs=epochs,
              shuffle=True,
              verbose=1)

    model.save_weights(os.path.join(output, f"knot_classifier_{time.time():.0f}"))
    model.save(os.path.join(output, f"knot_classifier_{time.time():.0f}.h5"))


def paint_bounding_boxes(image, bboxes, **kwargs):
    output_image = image.copy()

    for x, y, w, h in bboxes.astype(int):
        output_image = cv2.rectangle(img=output_image, pt1=(x, y), pt2=(x + w, y + h), **kwargs)

    return output_image


def predictions_test(data: str, out: str):
    image_files = sorted(glob.glob(os.path.join(data, "*.png")), key=image_file_sorter)

    model = tf.keras.models.load_model(out)

    y_preds = []

    for image_file in image_files:
        image = cv2.imread(image_file)
        predict_image = image.copy() / 255.
        y_pred = model.predict(predict_image[np.newaxis, ...])

        x, y, w, h = y_pred[0]
        image_height, image_width, _ = image.shape

        x = x * image_width
        w = w * image_width
        y = y * image_height
        h = h * image_height

        image = paint_bounding_boxes(image, np.array([[x, y, w, h]]).astype(int), color=(0, 255, 0))
        file_name = os.path.basename(image_file)
        cv2.imwrite(os.path.join("outfiles", file_name), image)


if __name__ == "__main__":
    import argparse

    def options():
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--data",
                            help="Dataset folder or pickle file",
                            required=True,
                            type=str)

        parser.add_argument("-o", "--output",
                            help="Path to save trained model weights",
                            required=True,
                            type=str)
        return parser

    args = options().parse_args()
    data = args.data
    output_folder = args.output

    # train(data, output_folder, epochs=50)
    predictions_test(data, output_folder)