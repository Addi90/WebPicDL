# WebPicDL #
A simple command line tool for downloading all supported image types from a webpage, written in python. It can filter for types and sizes.

## How to Use ##
Open the command line and call picloader.py with the first argument being the target URL or a text file having target URLs. The URLs in the file must be each in a new line. Commas and other separators not needed, just each in their own line. 

Attribute|Description
:---:|:---
-o *PATH*|Save images to specified path instead working directory (optional)
-n *NAME*|Search for images with a specific name, * for wildcard (e.g. \"image*\" for files like image123.jpg), other Regex are possible (optional)
-G|Attempts to get the source image from image galleries
-p|filter for *.png (optional)
-j|filter for *.jpg (optional)
-g|filter for *.gif (optional)
--min-size *X Y*|only images of a minimum size of X * Y Pixels
--max-size *X Y*|only images of a maximum size of X * Y Pixels

All pictures will be saved in the current working directory if savepath is not specified (-o).
Image Type Filters can be combined (Ex.: -jg for jpgs and gifs), size filters --min-size and --max-size can also be used at once.
- - - -
Example downloading only jpegs of minimum 200x200 Pixels to specified directory:
```
    picloader.py http://www.exampleurl... -j -o C:/Exampledir/ --min-size 200 200
```
Example downloading gallery images from URLs in a text file of minimum 1000x1000 pixels with a name starting with "img"
```
    picloader.py  source.txt -n img* -G --min-size 1000 1000
```

