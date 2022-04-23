import argparse
import glob
import json
import os.path
import pickle

import numpy as np
import cv2.cv2 as cv2

import imgaug.augmenters as iaa
from imgaug.augmentables.segmaps import SegmentationMapsOnImage

from src.image_tools import get_bounding_boxes, image_file_sorter, paint_bounding_boxes, image_dir_sorter


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


def get_file_metadata(meta_data: dict, key: str):
    for k in meta_data.keys():
        if k.startswith(key):
            return meta_data[k]

    return None


def prepare_images(images_folder, anomaly_type):
    image_base_folder = 'image'
    masks_base_folder = 'masks'

    meta_file = os.path.join(images_folder, "annot.json")
    meta_data = json.load(open(meta_file, 'r'))

    images = []
    images_masks = []

    for key in meta_data:
        meta_file = meta_data[key]
        file_id, ext = os.path.splitext(meta_file['filename'])
        image_file = os.path.join(images_folder, file_id, image_base_folder, meta_file['filename'])
        image = cv2.imread(image_file)
        images.append(image)

        mask = np.zeros(image.shape[:-1], dtype=np.uint8)

        for j, region in enumerate(meta_file['regions']):
            if region['region_attributes']['type'] == anomaly_type:
                mask_file = os.path.join(images_folder, file_id, masks_base_folder, f"{file_id}_{j}.png" )
                mask_data = cv2.imread(mask_file, cv2.COLOR_BGR2GRAY)
                mask_data[mask_data > 200] = 255
                mask += mask_data

        if len(mask) > 0:
            masks_on_image = SegmentationMapsOnImage(np.array(mask), image.shape)
            images_masks.append(masks_on_image)
        else:
            images_masks.append(None)

    return images, images_masks


def augment_images(images_folder: str, anomaly_type: str, number_of_augmentations: int = 10):
    augmenter = define_augmentations()
    images, segmaps = prepare_images(images_folder, anomaly_type)

    all_images = []
    all_segmaps = []

    for i in range(number_of_augmentations):
        augmented_images, augmented_segmaps = augmenter(images=images, segmentation_maps=segmaps)
        all_images += augmented_images

        for augmented_segmap in augmented_segmaps:
            all_segmaps += [augmented_segmap.get_arr()]

    return all_images, all_segmaps


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
    input_folder = args.input
    output_folder = args.output
    num_aug = args.n

    # generate augmented dataset
    for anomaly_type in ['knot', 'crack', 'stain']:
        print(f"Augmenting images for {anomaly_type} ...")
        images, segmaps = augment_images(input_folder, number_of_augmentations=num_aug, anomaly_type=anomaly_type)

        # save as pickle file
        with open(os.path.join(output_folder, f"train_augmented_{anomaly_type}.pkl"), 'wb') as pickle_file:
             pickle.dump({
                 'images': images,
                 'segmaps': segmaps
             }, pickle_file)

             pickle_file.close()

        folder = os.path.join(output_folder, anomaly_type)
        if not os.path.exists(folder):
            os.mkdir(folder)

        for i, image in enumerate(images):
            segmap = segmaps[i]
            image_file = f"{i}.png"
            segmap_file = f"{i}_segmap.png"

            cv2.imwrite(os.path.join(folder, image_file), image)
            cv2.imwrite(os.path.join(folder, segmap_file), segmap)


    # # load pickle file
    # TODO: This should be in a test
    # with open(os.path.join(output_folder, "train_augmented.pkl"), 'rb') as pickle_file:
    #     data = pickle.load(pickle_file)
    #     pickle_file.close()
    #
    # images = data['images']
    # bboxes = data['bboxes']

    # paint bounding boxes and save images
    # for i, image in enumerate(images):
    #     image_bboxes: BoundingBoxesOnImage = bboxes[i]
    #     image_bboxes_rects = image_bboxes.to_xyxy_array()
    #
    #     image = paint_bounding_boxes(image, image_bboxes_rects, color=(255, 0, 0), thickness=1)
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     cv2.imwrite(os.path.join(output_folder, f"{i}.png"), image)

    print(f"{len(images)} augmented images ready")
