import argparse
import glob
import os.path
import pickle

import numpy as np
import cv2.cv2 as cv2

import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from src.image_tools import get_bounding_boxes, image_file_sorter, paint_bounding_boxes


def define_augmentations():
    seq = iaa.Sequential([
        iaa.Fliplr(0.5),  # horizontal flips
        iaa.Flipud(0.5),

        # Small gaussian blur with random sigma between 0 and 0.5.
        iaa.Sometimes(
            0.5,
            iaa.GaussianBlur(sigma=(0, 0.5))
        ),

        # Strengthen or weaken the contrast in each image.
        iaa.LinearContrast((0.75, 1.5)),

        # Add gaussian noise.
        iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05 * 255), per_channel=0.5),

        # Make some images brighter and some darker.
        iaa.Multiply((0.8, 1.2), per_channel=0.2),
    ], random_order=True)

    return seq


def prepare_images(images_folder):
    image_files = sorted(glob.glob(os.path.join(images_folder, "*.png")), key=image_file_sorter)

    images = []
    bboxes = []

    for image_file in image_files:
        image_file_base = os.path.basename(image_file)
        image_file_name, ext = os.path.splitext(image_file_base)
        image = cv2.imread(os.path.join(images_folder, image_file_base))
        images.append(image)

        gt_file = os.path.join(images_folder, f"{image_file_name}.reg")
        if os.path.exists(gt_file):
            bounding_boxes = get_bounding_boxes(gt_file)
            bounding_boxes_on_image = []

            for x, y, w, h in bounding_boxes:
                bounding_box = BoundingBox(x, y, x + w, y + h)
                bounding_boxes_on_image.append(bounding_box)

            bboxes.append(BoundingBoxesOnImage(bounding_boxes_on_image, image.shape))
        else:
            bboxes.append(BoundingBoxesOnImage([], image.shape))

    return images, bboxes


def augment_images(images_folder: str, number_of_augmentations: int = 10):
    augmenter = define_augmentations()
    images, bboxes = prepare_images(images_folder)

    all_images = []
    all_bboxes = []

    for i in range(number_of_augmentations):
        augmented_images, augmented_bboxes = augmenter(images=images, bounding_boxes=bboxes)
        all_images += augmented_images
        all_bboxes += augmented_bboxes

    return all_images, all_bboxes


if __name__ == "__main__":
    import argparse

    def options():
        parser = argparse.ArgumentParser()

        parser.add_argument("-i", "--input",
                            help="Input folder with images and ground truth",
                            required=True,
                            type=str)

        parser.add_argument("-o", "--output",
                            help="Output folder, generated data will be here",
                            required=True,
                            type=str)

        parser.add_argument("-n",
                            help="Number of augmentation iterations to do",
                            type=int,
                            default=10)

        return parser

    args = options().parse_args()
    folder = args.input
    output_folder = args.output
    num_aug = args.n

    # generate augmented dataset
    print(f"Augmenting images...")
    images, bboxes = augment_images(folder, number_of_augmentations=num_aug)

    # save as pickle file
    with open(os.path.join(output_folder, "train_augmented.pkl"), 'wb') as pickle_file:
         pickle.dump({
             'images': images,
             'bboxes': bboxes
         }, pickle_file)
         pickle_file.close()

    # # load pickle file
    # TODO: This should be in a test
    # with open(os.path.join(output_folder, "train_augmented.pkl"), 'rb') as pickle_file:
    #     data = pickle.load(pickle_file)
    #     pickle_file.close()
    #
    # images = data['images']
    # bboxes = data['bboxes']

    # paint bounding boxes and save images
    for i, image in enumerate(images):
        image_bboxes: BoundingBoxesOnImage = bboxes[i]
        image_bboxes_rects = image_bboxes.to_xyxy_array()

        image = paint_bounding_boxes(image, image_bboxes_rects, color=(255, 0, 0), thickness=1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(output_folder, f"{i}.png"), image)

    print(f"{len(images)} augmented images ready")
