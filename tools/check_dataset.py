import glob
import os.path
import yaml

import numpy as np
import cv2.cv2 as cv2


def file_sorter(file):
    dir = os.path.dirname(file)
    f, ext = os.path.splitext(os.path.basename(file))
    return f"{dir}{int(f):05d}"


if __name__ == "__main__":
    source_folder = "../muestras"
    output_folder = "../output"

    files = sorted(glob.glob(os.path.join(source_folder, "**", "*.png"), recursive=True), key=file_sorter)
    f = cv2.FileStorage()

    for i, filepath in enumerate(files):
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        file, ext = os.path.splitext(filename)
        gt_file = os.path.join(dirname, f"{file}.reg")

        if os.path.exists(gt_file):
            f.open(gt_file, cv2.FILE_STORAGE_READ)
            gt_data = f.getNode('rectangles').mat()

            image = cv2.imread(filepath)

            for rect_idx in range(0, gt_data.shape[1]):
                x, y, width, height = gt_data[:, rect_idx]
                image = cv2.rectangle(image, pt1=(x, y), pt2=(x + width, y + height), color=(0, 255, 0))

            outdir = os.path.join(output_folder, os.path.split(dirname)[-1])
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            cv2.imwrite(os.path.join(outdir, filename), image)

        else:
            print(f"File {filepath} does not have ground truth")
