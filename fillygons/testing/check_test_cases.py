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
    image.paste(overlay, None, overlay)


def main(rendered_image_paths):
    failed_cases = []

    for rendered_image_path in rendered_image_paths:
        base_path, suffix = os.path.splitext(rendered_image_path)

        expected_image_path = base_path + '-expected' + suffix
        failure_image_path = base_path + '-failure' + suffix

        rendered_image = Image.open(rendered_image_path).convert('L')
        expected_image = Image.open(expected_image_path).convert('L')

        images_match = list(rendered_image.getdata()) == list(expected_image.getdata())

        if images_match:
            if os.path.exists(failure_image_path):
                os.unlink(failure_image_path)
        else:
            paste_with_transparency(expected_image, get_overlay('expected'))
            paste_with_transparency(rendered_image, get_overlay('actual'))

            failure_image = Image.merge('RGB', [expected_image, rendered_image, expected_image])

            os.makedirs(os.path.dirname(failure_image_path), exist_ok=True)
            failure_image.save(failure_image_path, 'PNG')

            failed_cases.append(base_path)

    if failed_cases:
        for i in failed_cases:
            print('Test case failed: {}'.format(i))

        print('{} of {} test cases failed.'.format(len(failed_cases), len(rendered_image_paths)))

        sys.exit(1)
    else:
        print('All {} test cases succeeded.'.format(len(rendered_image_paths)))


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('rendered_image_paths', nargs=REMAINDER)

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
