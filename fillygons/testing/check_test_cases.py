import os
import sys
from argparse import ArgumentParser, REMAINDER

import pkg_resources
from PIL import Image


def get_overlay(name):
    stream = pkg_resources.resource_stream(
        __name__,
        'resources/overlay_{}.png'.format(name))

    return Image.open(stream).convert()


def paste_with_transparency(image, overlay):
    # Use the image itself as the mask.
    image.paste(overlay, None, overlay)


def main(actual_image_paths):
    num_test_cases = len(actual_image_paths)
    num_failures = 0

    for actual_image_path in actual_image_paths:
        base_path, suffix = os.path.splitext(actual_image_path)
        expected_image_path = base_path + '-expected' + suffix
        failure_image_path = base_path + '-failure' + suffix

        if not os.path.exists(expected_image_path):
            print('Error: Image with expected output not found: {}'.format(expected_image_path))
            num_failures += 1

            continue

        actual_image = Image.open(actual_image_path).convert('L')
        expected_image = Image.open(expected_image_path).convert('L')

        images_match = list(actual_image.getdata()) == list(expected_image.getdata())

        if images_match:
            if os.path.exists(failure_image_path):
                os.unlink(failure_image_path)
        else:
            paste_with_transparency(expected_image, get_overlay('expected'))
            paste_with_transparency(actual_image, get_overlay('actual'))

            failure_image = Image.merge('RGB', [expected_image, actual_image, expected_image])

            os.makedirs(os.path.dirname(failure_image_path), exist_ok=True)
            failure_image.save(failure_image_path, 'PNG')

            print('Error: Test case failed: {}'.format(failure_image_path))
            num_failures += 1

    if num_failures:
        print('\x1b[1;31m{} of {} test cases failed.\x1b[m'.format(num_failures, num_test_cases))

        sys.exit(1)
    else:
        print('\x1b[1;32m{} test cases succeeded.\x1b[m'.format(num_test_cases))


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        'actual_image_paths',
        nargs=REMAINDER,
        help='Paths to the images containing the actual, rendered output.')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
