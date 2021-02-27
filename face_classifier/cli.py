"""Console script for face_classifier."""

import os
import sys
import shutil
import matplotlib.pyplot as plt
import click
import face_recognition
from PIL import UnidentifiedImageError

CLASSIFIER_PATH = "FACE_CLASSIFIER"
CLASSIFIER_PREFIX = "FACE_"


def classifier(path):
    print(f'* The images absolute path:', path)

    c = click.get_current_context()
    path = c.params["path"]
    images = []

    ''' Create the directory for face classification'''
    classifier_path = path + '/' + CLASSIFIER_PATH
    if os.path.exists(classifier_path):
        shutil.rmtree(classifier_path)

    try:
        os.mkdir(classifier_path)
    except OSError:
        print("Creation of the directory %s failed" % classifier_path)
        quit()
    else:
        print("Successfully created the directory: %s " % classifier_path)

    """Check if images are valid and print the number of images."""
    print('* Check if images are valid and print the number of images.')
    g = os.walk(path)
    images_count = 0
    for ab_path, dir_list, file_list in g:
        for file_name in file_list:
            try:
                plt.imread(ab_path + '/' + file_name)
                image_path = ab_path + '/' + file_name
                images.append(image_path)
                images_count += 1
            except UnidentifiedImageError as err:
                print('\t\033[31m' + str(err) + '\033[0m')

    print(f'* Total images: ', images_count)

    bitmap = bytearray(len(images))
    image_dir_index = 0
    for image_index in range(len(images)):
        if bitmap[image_index] == 0x01:
            continue

        bitmap[image_index] = 0x01
        image_index_path = classifier_path + '/' + CLASSIFIER_PREFIX + str(image_dir_index)
        try:
            os.mkdir(image_index_path)
        except OSError:
            print("Creation of the directory %s failed" % image_index_path)
            quit()
        else:
            print("Successfully created the directory %s " % image_index_path)
            image_dir_index += 1

        raw_image = face_recognition.load_image_file(images[image_index])
        shutil.copy(images[image_index], image_index_path)
        unknown_images = []

        for unknown_image_index in range(image_index+1, len(images)):
            unknown_image = face_recognition.load_image_file(images[unknown_image_index])
            unknown_images.append(unknown_image)

        unknown_images_encoding = []
        try:
            raw_image_encoding = face_recognition.face_encodings(raw_image)[0]
        except IndexError:
            print("It wasn't able to locate any faces in raw image %s" % images[image_index])
            continue

        for unknown_image_index in range(len(unknown_images)):
            try:
                unknown_image_encoding = face_recognition.face_encodings(unknown_images[unknown_image_index])[0]
                unknown_images_encoding.append(unknown_image_encoding)
            except IndexError:
                print("It wasn't able to locate any faces in raw image %s" %
                      images[image_index+unknown_image_index])
                continue

        known_faces = [
            raw_image_encoding
         ]

        for unknown_image_encoding_index in range(len(unknown_images_encoding)):
            result = face_recognition.compare_faces(known_faces, unknown_images_encoding[unknown_image_encoding_index],
                                                    tolerance=0.7)
            if result[0]:
                shutil.copy(images[image_index+unknown_image_encoding_index+1], image_index_path)
                bitmap[image_index+unknown_image_encoding_index+1] = 0x01

    print("* Finished.")


@click.command()
@click.option('--path', help='The images absolute path.')
def main(path):
    """Console script for face_classifier."""
    classifier(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
