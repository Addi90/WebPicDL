# WebPicDL #
A simple command line tool for downloading all .jpg and .png images from a webpage, written in python.

## How to Use ##
Open the command line and call picloader.py with the first argument being the target URL

Attribute|Description
:---:|:---
-o|Save images to specified path (optional)
-p|filter for *.png (optional)
-j|filter for *.jpg (optional)

- - - -
Example downloading only jpegs to specified directory:
    _picloader.py http://www.exampleurl... -j -o C:/Exampledir/_

All pictures will be saved in the current working directory if savepath is not specified (-o).
Without filter, every datatype of image will be saved.
