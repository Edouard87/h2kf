'''
A formatting tool for photos for submission to h2k.
'''
import argparse
import logging
from datetime import datetime

from src.image import process_images

def main():
    p = argparse.ArgumentParser(description=__doc__)
    image_p = p.add_subparsers(help='''
        Image subprocessing.
    ''')
    image_p.add_argument('directory', help='''
        The directory the tool should scan to find the images.
    ''')
    image_p.add_argument('output', help='''
        The directory in which the tool should output the formatted images.
    ''')
    image_p.add_argument('file_id', help='''
        The ID of the file to be set as the name for every image.
    ''')
    image_p.add_argument("--size", help='''
        The size of the output images.
    ''')
    image_p.add_argument('--skip-not-images', action='store_true', help='''
        Skip files in directory that are not images. Default to true.
    ''')
    image_p.add_argument('--verbose', '-v', action='count', help='''
        Log level. The more the letter appears, the higher the count.
    ''')
    image_p.add_argument('--date', help='''
        The date to print on each image. Will default to the current date if not specified. The application does not
        complete any formatting.
    ''')
    args = p.parse_args()

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

    DATE_FORMAT: str = "%d-%B-%Y"

    if not args.date:
        now       = datetime.now()
        args.date = now.strftime(DATE_FORMAT)

    process_images(
        src_directory = args.directory,
        out_directory = args.output,
        file_id       = args.file_id,
        date          = args.date
    )

if __name__ == "__main__":
    main()