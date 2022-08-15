# H2K Formatter

usage: h2kf.py [-h] [--verbose] {image} ...

A formatting tool for photos for submission to h2k.

positional arguments:
  {image}        Application processing subcontexts. Currently can only be `image`.
    image        Image processing context.

options:
  -h, --help     show this help message and exit
  --verbose, -v  The verbosity of the application. Use `-vvvv` for most verbose.

## Image Processing Context

usage: h2kf.py image [-h] [--date DATE] [--output-format {PNG,JPG,HEIC}] [--generate-timestamp] src_directory out_directory file_id

positional arguments:
  src_directory         The directory the tool should scan to find the images.
  out_directory         The directory in which the tool should output the formatted images.
  file_id               The ID of the file to be set as the name for every image. Also stamped into the image next to the date.

options:
  -h, --help            show this help message and exit
  --date DATE           The date to print on each image. Will default to the current date if not specified. The application does not    
                        complete any formatting.
  --output-format {PNG,JPG,HEIC}
  --generate-timestamp  Whether the application should use the file metadata to generate the timestamp.
