import unittest
import os
import datetime
from unittest import mock
from copy import copy

from src.h2kf.image import process_images

'''
NOTE: Do not extend the classes from `wand` because it will get complicated. `wand` will try to instantiate an instance of the
`wand` binary (which is ImageMagick), which is exactly what we don't want.
'''

# Global Constants

CTIME: float        = 1660184036.3148046 # August 10th, 2022 at 10:13
ORIGINAL_SIZE: int  = 5605101            # 5 Mb
CONVERTED_SIZE: int = 866115             # 0.87 Mb
SRC_DIR: str        = "/src/directory/"
OUT_DIR: str        = "/out/directory/"
FILE_ID: str        = "2D45789"
AMOUNT_FILES: int   = 10
FILENAME_PATTERN: str = "file %i" 
SRC_FMT: str        = "PNG"
OUT_FMT: str        = "JPG"

# Global Variables

images: list        = {} # Emulate filesystem storage.

class m_Image:
    '''
    Mock class for image used throughout tests.
    '''
    def __init__(self, filename: str):
        self.filename: str                   = filename
        # Simulating an actual image.
        self.width: int                      = 4032
        self.height: int                     = 3024
        self.resolution: tuple[float, float] = (72.0, 72.0)
        self.format: str                     = os.path.splitext(self.filename)[1][1:]
        # Simulating a drawing
        self._m_drawing                      = None
        # Simulating saving
        self._m_saved: bool                  = False
        self._m_filesize                     = ORIGINAL_SIZE
        # Make the file exist
        self.save(filename)
        # super().__init__(wand = None)
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass
    def convert(self, output_format):
        c = copy(self)
        c.format   = output_format
        c._m_saved = False
        return c
    def resample(self, width: float, height: float):
        self.resolution  = (float(width), float(height))
        self._m_filesize = CONVERTED_SIZE # simultate change in size.
    def save(self, filename: str = ""):
        # NOTE: filename is actually filepath.
        self._m_saved = True
        self.filename = filename
        images.update({self.filename: self})
    
class m_Drawing:
    '''
    Mock class for the drawing instance.
    '''
    def __init__(self) -> None:
        self.font: str         = ""
        self.fill_color: str   = ""
        self.stroke_color: str = ""
        self.font_size: int    = 0
        self.x: int            = 0
        self.y: int            = 0
        self.body: str         = ""
    def text(self,
        x: int        = 0,
        y: int        = 0,
        body: str     = "") -> None:
            self.x    = x
            self.y    = y
            self.body = body

    def draw(self, image: m_Image):
        image._m_drawing = self

    def __call__(self, image):
        self.draw(image)
    
    def __enter__(self):
        '''
        See source code of `wand.resource` for implementation of `Resource` class used for
        `Draw`.
        '''
        return self
    
    def __exit__(self, type, value, traceback):
        '''
        Nothing to do as the object does not actually exist.
        '''
        pass

class m_file:
    def __init__(self, name: str, path: str):
        self.name: str = name
        self.path: str = path

class m_scandir_base():
    '''
    Base class implementing scandir without proper file suffixes. This will result in errors as the files
    do not have the appropriate extensions.
    '''
    def __init__(self, dir: str):
        self.dir = dir
        self.suffix = "" # useful for testing
    def __enter__(self):
        _files = []
        for i in range(0, AMOUNT_FILES):
            _name = FILENAME_PATTERN % i + self.suffix
            _files.append(m_file(
                name = _name,
                path = os.path.join(self.dir, _name)
            ))
        return _files
    def __exit__(self, type, value, traceback):
        pass

class m_scandir_JPG(m_scandir_base):
    def __init__(self, dir: str):
        self.dir = dir
        self.suffix = f".{SRC_FMT}"

def m_getctime(path: str) -> float:
    '''
    Return an arbitrary ctime defined by a global variable. The `path` does not matter.
    '''
    return CTIME

def m_getsize(filepath: str):
    '''
    Mock of the `getsize` method. Returns an arbitary size for testing purposes. Note that the size
    returned is in bytes.
    '''
    try:
        return images[filepath]._m_filesize
    except KeyError:
        raise FileNotFoundError(f"The system canno find the file specified: '{filepath}'") # if the file does not exist.

def _get_mock_name(mock: mock.MagicMock) -> str:
    return vars(mock)['_mock_name']

@mock.patch('src.h2kf.image.Image',            side_effect = m_Image)
@mock.patch('src.h2kf.image.Drawing',          side_effect = m_Drawing)
@mock.patch('src.h2kf.image.os.path.getctime', side_effect = m_getctime)
@mock.patch("src.h2kf.image.os.path.getsize",  side_effect = m_getsize)
class TestConvert(unittest.TestCase):
    @mock.patch('src.h2kf.image.os.scandir',   side_effect = m_scandir_JPG)
    def test_convert_ok(self, *args):
        process_images(
            src_directory      = SRC_DIR,
            out_directory      = OUT_DIR,
            generate_timestamp = True,
            output_format      = OUT_FMT,
            file_id            = FILE_ID
        )
        arg: mock.MagicMock
        for arg in args:
            if _get_mock_name(arg) == 'scandir':
                arg.assert_called_with(SRC_DIR)
                arg.assert_called_once()
            elif _get_mock_name(arg) == 'Image':
                self.assertEqual(arg.call_count, AMOUNT_FILES)
            elif _get_mock_name(arg) == 'Drawing':
                self.assertEqual(arg.call_count, AMOUNT_FILES)
                for call in arg.call_args_list:
                    self.assertEqual(call, ())
            elif _get_mock_name(arg) == 'getctime':
                '''
                `getctime` is called once per source file to get the time and create
                a timestamp.
                '''
                self.assertEqual(arg.call_count, AMOUNT_FILES)
                for index, call in enumerate(arg.call_args_list):
                    self.assertEqual(call, (os.path.join(SRC_DIR,f"{FILENAME_PATTERN % index}.{SRC_FMT}"),))
                print(arg)
        print('done')
