'''
Source code for the h2k-format application.
'''
import os
import logging
import re
from datetime import datetime

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import wand.version as wver

from typing import Union

class ProcessException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

def process_images(
    src_directory: str, 
    out_directory: str,
    file_id: str,
    date: Union[str, None]             = None,
    generate_timestamp: bool           = True,
    font: str                          = "Arial",
    output_format: str                 = "JPG",
    offset: int                        = 5,
    stamp_size: float                  = None,
    stamp_color                        = "#FFFFFF",
    stamp_border_color                 = "#000000",
    stamp_border_width                 = 1,
    output_resolution: tuple[int, int] = None) -> None:
    '''
    Process the provided images, appling the transformations.
    Will automatically format the `datetime` with the ISO format suing `strftime`.

    :param: src__directory (str)   -- The directory of images to scan.
    :param: out_directory  (str)   -- The directory where processed images should be dumped.
    :param: date           (str)   -- The date to stamp on images.
    :param: file_id        (str)   -- The ID of the file to output.
    :param: font           (str)   -- The path of a custom font to use.
    :param: stamp_size     (int)   -- The size of the date stamp in terms of pixels.

    :return: None
    '''

    if date and generate_timestamp: raise ValueError('''Cannot generate timestamp 
        and provide date. Either `date` must be `None`
        or `generate_timestamp` must be `False`.''')
    
    if not wver.fonts(font):
        raise ValueError(f"Font {font} not supported by system.")
    if not wver.formats(output_format.upper()):
        raise ValueError(f"Image output format {output_format} not supported by system.")
    if not date and not generate_timestamp:
        raise ValueError("Must either provide `date` or `timestamp`.")
    if output_resolution:
        if not type(output_resolution) is tuple and not type(output_resolution) is list:
            raise TypeError("`output_resolution` must be a tuple of (x-res, y-res).")
        if len(output_resolution) != 2:
            raise ValueError("`output_resolution must of a 2-tuple.")

    logger = logging.getLogger(__name__)

    IMAGE_PATTERN: str = "(\.png)|(\.jpg)|(\.heic)|(\.jpeg)$"

    try:
        with os.scandir(src_directory) as dl:
            for index, file in enumerate(dl):
                if not re.search(IMAGE_PATTERN,file.name, re.IGNORECASE):
                    logger.warning('Skipping file {} as it is not an image.'.format(file.name))
                    continue
                with Image(filename = file.path) as original:
                    if generate_timestamp:
                        date = datetime.fromtimestamp(os.path.getctime(file.path)).strftime("%d-%m-%Y")
                        logger.debug(f"Generated timestamp {date} for image {file.name}")
                    logger.info(f"Converting image {file.name} of size {original.width}x{original.height}")
                    converted: Image = original.convert(output_format)
                    if not stamp_size:
                        stamp_size = original.height * 0.05
                    if not output_resolution:
                        logger.debug('''Attempting to guess output resolution
                            of image as image resolution was not set. Original
                            image resolution is %ix%i. Note that this also affects
                            stamp_size and `stamp_border_width`''' % converted.resolution)
                        res = max(converted.resolution)
                        if res <= 72:
                            output_resolution  = (25,25)
                            stamp_size         = 0.03 * original.height
                            stamp_border_width = 1
                            offset             = 5
                        elif res <= 102:
                            output_resolution  = (70,70)
                            stamp_size         = 0.03 * original.height
                            stamp_border_width = 2
                            offset             = 10
                        elif res <= 500:
                            output_resolution  = (200,200)
                            stamp_size         = 0.03 * original.height
                            stamp_border_width = 2
                            offset             = 20
                            logger.info("Image resolution is large. Consider explicitly supplying a different output resolution with `--output-resolution`.")
                        else:
                            raise ValueError("`output_resolution` must be specified for image of a resolution larger than 500 on either dimension.")
                        logger.debug("Applying resolution %ix%i to output." % output_resolution)
                    converted.resample(*output_resolution)
                    with Drawing() as draw:
                        draw.font = font
                        draw.fill_color = Color(stamp_color)
                        draw.stroke_color = Color(stamp_border_color)
                        draw.stroke_width = stamp_border_width
                        draw.font_size  = stamp_size
                        draw.text(offset, converted.height - offset, f"{date} {file_id}")
                        draw(converted)
                    output_path = "{} - {}.{}".format(os.path.join(out_directory,file_id), index + 1, output_format)
                    converted.save(filename=output_path)
                    initial_size = os.path.getsize(file.path) / 1000000 # size in Mb
                    final_size   = os.path.getsize(output_path) / 1000000 # size in Mb
                    logger.debug(f"Reduced size of file {file.name} from {initial_size} to {final_size}")
    except FileNotFoundError as e:
        raise ValueError(f"Directory {src_directory} does not exist")