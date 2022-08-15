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
    offset: int                        = 20,
    stamp_size: float                  = 0.05,
    timestamp_color                    = "#FFFFFF",
    timestamp_border_color             = "#000000",
    output_resolution: tuple[int, int] = (25, 25)) -> None:
    '''
    Process the provided images, appling the transformations.
    Will automatically format the `datetime` with the ISO format suing `strftime`.

    :param: src__directory (str)   -- The directory of images to scan.
    :param: out_directory  (str)   -- The directory where processed images should be dumped.
    :param: date           (str)   -- The date to stamp on images.
    :param: file_id        (str)   -- The ID of the file to output.
    :param: font           (str)   -- The path of a custom font to use.
    :param: size           (tuple) -- A 2-tuple representing the width and height to be removed from images when processed.
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
                    converted.resample(*output_resolution)
                    with Drawing() as draw:
                        draw.font = font
                        draw.fill_color = Color(timestamp_color)
                        draw.stroke_color = Color(timestamp_border_color)
                        draw.font_size  = converted.height * stamp_size
                        draw.text(offset, converted.height - offset, f"{date} {file_id}")
                        draw(converted)
                    output_path = "{} - {}.{}".format(os.path.join(out_directory,file_id), index + 1, output_format)
                    converted.save(filename=output_path)
                    initial_size = os.path.getsize(file.path) / 1000000 # size in Mb
                    final_size   = os.path.getsize(output_path) / 1000000 # size in Mb
                    logger.debug(f"Reduced size of file {file.name} from {initial_size} to {final_size}")
    except FileNotFoundError as e:
        raise ValueError(f"Directory {src_directory} does not exist")