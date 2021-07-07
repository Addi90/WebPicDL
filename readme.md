# WebPicDL #
A simple command line tool for downloading all supported image types from a webpage, written in python. It can filter for types and sizes.

## How to Use ##
Open the command line and call picloader.py with the first argument being the target URL. 

Attribute|Description
:---:|:---
-o *PATH*|Save images to specified path (optional)
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

