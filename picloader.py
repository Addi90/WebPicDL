from io import BytesIO
from os import access,path
import sys
import optparse
import urllib
import requests
import re

from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession


def main(argv):
    try: 
        url = argv[1]
    except IndexError as e:
        print(f"{e}: no target URL entered - exiting...")
        return
    parser = optparse.OptionParser()
    filetypes = parser.add_option_group("filetypes")
    sizelimits = parser.add_option_group("sizelimits")
    init_optparser(parser,filetypes,sizelimits)

    args, remainder = parser.parse_args()
    print("getting images from: " + url)
    compat_types = [".jpg",".png",".gif"]

    if not args.chosen_types:
        chosen_types = compat_types
    else: 
        chosen_types = args.chosen_types
    savepath = args.o

    url_list = get_img_urls(url)
    if args.G:
        gallery_url_list = get_gallery_img_urls(url)
        url_list.extend(gallery_url_list)

    img_url_list = filter_compat_urls(url_list,chosen_types)
    count = 0
    for url in img_url_list:
        try:
            img = get_img(url)

            if args.min_s and args.max_s:    
                if filter_min_size(img,args.min_s) and filter_max_size(img,args.max_s):
                    save_img(img, url.rsplit('/', 1)[1],savepath)
            elif args.min_s:
                if filter_min_size(img,args.min_s):
                    save_img(img, url.rsplit('/', 1)[1],savepath)
            elif (args.max_s != None):
                if filter_max_size(img,args.max_s):
                    save_img(img, url.rsplit('/', 1)[1],savepath)
            else:
                save_img(img, url.rsplit('/', 1)[1],savepath)
            count += 1
        except Exception as e:
            print(e)
    
    print("finished downloading {} images!".format(count))


# Initializes all possible command-line options

def init_optparser(parser,filetypegroup,sizelimitgroup):

    # Output Directory
    parser.add_option('-o',
        help="Set Output Directory for downloaded Images."
        "If not set, Output Directory will be current Directory",
        action="store"
        )

    parser.add_option('-G',
        "--Gallery",help="tries to download the source images in a gallery of thumbnails",
        action="store_true",
        dest="G"
        )

    # Filter for Filetypes
    filetypegroup.add_option('-g',"--gif",
        help="Filter for .gif Images,"
        "can be combined with other Imagetype Filters",
        action="append_const",
        const=".gif",
        dest="chosen_types"
        )                
    filetypegroup.add_option('-j',"--jpeg",
    help="Filter for .jpeg Images,"
        "can be combined with other Imagetype Filters",   
        action="append_const",
        const=".jpg",
        dest="chosen_types"
        )
    filetypegroup.add_option('-p',"--png",
        help="Filter for .png Images,"
        "can be combined with other Imagetype Filters",
        action="append_const",
        const=".png",
        dest="chosen_types"
        )

    # Set min. and max. Image Size
    sizelimitgroup.add_option("--min-size",
        metavar="WIDTH HEIGHT",
        help="All images sized above the chosen WIDTH and HEIGHT" 
        "in Pixels, can be combined with --max-size",
        type=int,
        nargs=2,
        dest="min_s",
        default=None
        )
    sizelimitgroup.add_option("--max-size",
        metavar="WIDTH HEIGHT",
        help="All images sized below the chosen WIDTH and HEIGHT" 
        "in Pixels, can be combined with --min-size",
        type=int,
        nargs=2,
        dest="max_s",
        default=None
        )


# Extract all absolute image-source-urls from the html code of given webpage url,
# returns list of image-source-urls

def get_gallery_img_urls(url : str):
    gallery_links = get_gallery_source_urls(url)
    gallery_img_links = []

    for glink in gallery_links:
        page_html = get_html(glink)

        for img_link in tqdm(
            re.findall(r'(?:http:\/|https:\/)?\/[^\"\']*\.(?:jpg|jpeg|gif|png)',page_html.html),
            "Extracting gallery source imagelinks"
            ):

            if img_link.find("html") == -1:
                img_link = urllib.parse.urljoin(glink,img_link)
            gallery_img_links.append(img_link)

    print(f"Found {len(gallery_img_links)} Links from Gallery")

    return gallery_img_links


def get_gallery_source_urls(url : str):
    page_html = get_html(url)
    elements = page_html.find('a')
    source_links = []
    for e in elements:
        if re.findall(r'<.*[\"\'](?:gallery.*|thumb.*)[\"\']\s?[>]',e.html):
            link = str(e.absolute_links)
            link = link[2:-2]
            source_links.append(link)
    #print(f"Gallery Source Links: {source_links}")

    return source_links


def get_img_urls(url : str):
    page_html = get_html(url)
    links = []

    for link in tqdm(
        re.findall(r'(?:http:\/|https:\/)?\/[^\"\']*\.(?:jpg|jpeg|gif|png)',page_html.html),
        "Extracting all imagelinks"
        ):

        link = urllib.parse.urljoin(url, link)
        links.append(link)

    links = remove_dupl_urls(links)
    print(f"Found {len(links)} Links")

    return links


def get_img(img_url):
    resp = requests.get(img_url)

    return Image.open(BytesIO(resp.content))


# Helper functions

def remove_dupl_urls(url_list : list):
    return list(dict.fromkeys(url_list))


def get_html(url : str):

    session = HTMLSession()
    resp = session.get(url)
        
    resp.html.render()
    return resp.html

# Saves image to given path 
# (if savepath=None: Save in current working directory)

def save_img(img,fname : str,savepath : str):
    if savepath == None:
        img.save(fname)
        print("Saving: {}".format(fname))
        return

    fpath = savepath+fname 
    img.save(fname)
    print("Saving {} to: {}".format(fname,fpath))
       

# Functions to filter a list of given Image-URLs for compatible formats

def check_compat(url : str,compat_types : list):
    for type in compat_types:
        if url.find(type) != -1:
            return True
    return False


def filter_compat_urls(url_list : list,compat_types : list):
    filtered_list = []
    for url in url_list:
        if check_compat(url,compat_types):
            filtered_list.append(url)
    print(f"Found {len(filtered_list)} compatible Image URLs")
    return filtered_list


# Filter images by given minimum and/or maximum size

def filter_min_size(img,size_limit):
    width, height = img.size
    if width > size_limit[0] and height > size_limit[1]:
        return True
    return False 


def filter_max_size(img,size_limit):
    width, height = img.size
    if width < size_limit[0] and height < size_limit[1]:
        return True
    return False 


if __name__ == "__main__":
    main(sys.argv)
