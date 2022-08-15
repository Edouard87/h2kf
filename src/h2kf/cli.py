'''
A formatting tool for photos for submission to h2k.
'''
import argparse
import logging
from datetime import datetime
from inspect import signature

from src.h2kf.image import process_images

import sys

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        prog = "h2kf.py")
    p.add_argument('--verbose',
        '-v',
        action = 'count',
        help="The verbosity of the application. Use `-vvvv` for most verbose.",
        default = 0)
    sub_p = p.add_subparsers(
        help     ='''Application processing subcontexts.
            Currently can only be `image`.
            ''',
        required = True)
    image_p = sub_p.add_parser('image', help = '''
        Image processing context.
    ''')
    image_p.add_argument('src_directory', help='''
        The directory the tool should scan to find the images.
    ''')
    image_p.add_argument('out_directory', help='''
        The directory in which the tool should output the formatted images.
    ''')
    image_p.add_argument('file_id', help='''
        The ID of the file to be set as the name for every image. Also stamped into the image
        next to the date.
    ''')
    def no_case_str(x: str):
        return x.upper()
    image_p.add_argument('--output-format',
        choices = ('PNG','JPG','HEIC'),
        type    = no_case_str,
        default = "JPG",
        help    = '''
            The format images should use in output. The default is `JPG`. Can be uppercase or lowercase.
        ''')
    date_g = image_p.add_mutually_exclusive_group(
        required = True)
    date_g.add_argument('--date', help='''
        The date to print on each image. Will default to the current date if not specified. The application does not
        complete any formatting.
    ''')
    date_g.add_argument('--generate-timestamp',
        help   = "Whether the application should use the file metadata to generate the timestamp.",
        action = "store_true")
    args = p.parse_args(sys.argv[1:])

    logger: logging.Logger = logging.getLogger(__name__)
    match args.verbose:
        case 0:
            logger.setLevel(logging.CRITICAL)
        case 1:
            logger.setLevel(logging.ERROR)
        case 2:
            logger.setLevel(logging.WARNING)
        case 3:
            logger.setLevel(logging.DEBUG)
        case 4:
            logger.setLevel(logging.INFO)
    
    f = logging.Formatter("%(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(f)
    logger.addHandler(sh)

    del args.verbose

    process_images(**vars(args))

if __name__ == "__main__":
    main()