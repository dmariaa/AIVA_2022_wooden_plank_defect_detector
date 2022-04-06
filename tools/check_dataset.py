import glob
import os.path
import cv2.cv2 as cv2

from src.image_tools import get_bounding_boxes, image_file_sorter

if __name__ == "__main__":
    source_folder = "../muestras"
    output_folder = "../output"
    file_sorter = image_file_sorter

    files = sorted(glob.glob(os.path.join(source_folder, "**", "*.png"), recursive=True), key=file_sorter)
    f = cv2.FileStorage()

    for i, filepath in enumerate(files):
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        file, ext = os.path.splitext(filename)
        gt_file = os.path.join(dirname, f"{file}.reg")

        if os.path.exists(gt_file):
            rects = get_bounding_boxes(gt_file)
            image = cv2.imread(filepath)

            for x, y, width, height in rects:
                image = cv2.rectangle(image, pt1=(x, y), pt2=(x + width, y + height), color=(0, 255, 0))

            outdir = os.path.join(output_folder, os.path.split(dirname)[-1])
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            cv2.imwrite(os.path.join(outdir, filename), image)

        else:
            print(f"File {filepath} does not have ground truth")
