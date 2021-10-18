from io import BytesIO
from os import access,path,mkdir,sep
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
        target_urls = get_targets(argv[1])
    except IndexError as e:
        print(f"{e}: no target URL entered - exiting...")
        return

    parser = optparse.OptionParser()
    filetypes = parser.add_option_group("filetypes")
    sizelimits = parser.add_option_group("sizelimits")
    init_optparser(parser,filetypes,sizelimits)

    args, remainder = parser.parse_args()
    compat_types = [".jpg",".png",".gif"]

    if not args.chosen_types:
        chosen_types = compat_types
    else: 
        chosen_types = args.chosen_types
    output_dir = args.o

    count = 0

    for url in target_urls:
        img_urls = []
        print(f"searching in {url}")
        if args.G:
            gallery_url_list = get_gallery_img_urls(url,args.n)
            img_urls.extend(gallery_url_list)
        else:
            img_urls.extend(get_img_urls(url,args.n))

        filtered_img_urls = filter_compat_urls(img_urls,chosen_types)
        
        if output_dir == None:
            i = 1
            while (path.isdir( sep.join(str(count+i)) + sep)):  
                i += 1
            mkdir(f"{count+i}")
            savepath = sep.join(str(count+i)) + sep
        else:
            i = 1
            while (path.isdir(output_dir + sep.join(str(count+i)) + sep)):  
                i += 1
            mkdir(f"{count+i}")
            savepath = output_dir + sep.join(str(count+i)) + sep
        print(f"saving images from {url} to ..{sep+savepath}")
        for url in tqdm(filtered_img_urls,"saving..."):
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
                
            except Exception as e:
                print(e)

        count += 1
    print(f"finished downloading images!")


# Initializes all possible command-line options

def init_optparser(parser,filetypegroup,sizelimitgroup):

    # Output Directory
    parser.add_option('-o',
        help="Set Output Directory for downloaded Images."
        "If not set, Output Directory will be current Directory",
        action="store"
        )

    # Set a File Name or part of a name to search for
    parser.add_option('-n',
        "--name",help="Search for images with a specific name, * for "
        "wildcard (e.g. \"image*\" for files like image123.jpg)",
        action="store",
        dest="n"
        )

    # Search for the source images of a image gallery
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

def get_gallery_img_urls(url : str, searchword : str = None):
    gallery_links = get_gallery_source_urls(url)
    gallery_img_links = []

    print(f"searching {len(gallery_links)} gallery source links")

    for glink in tqdm(gallery_links, "extracting source image links from gallery"):
        img_links = get_img_urls(glink,searchword)
        gallery_img_links.extend(img_links)
        
    print(f"found {len(gallery_img_links)} image links from gallery")

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


def get_img_urls(url : str, pattern : str = None ):
    page_html = get_html(url)
    links = []
    if(pattern == None):
        pattern = "*"

    for link in re.findall(r'(http\:\/\/|https\:\/\/)?([a-zA-Z0-9\-\.\_]+\.[a-zA-Z]{2,3})(\/\S*?)(\.jpg|\.jpeg|\.gif|\.png){1}',page_html.html):
        link = ''.join(map(str, link))
        if re.match(re.escape(pattern),link.rsplit('/', 1)[1]) != None:
            link = urllib.parse.urljoin(url, link)
            links.append(link)

    links = remove_dupl_urls(links)
    return links


def get_img(img_url):
    resp = requests.get(img_url,stream=True)

    return Image.open(BytesIO(resp.content))


# Helper functions

def remove_dupl_urls(url_list : list):
    return list(dict.fromkeys(url_list))


def get_html(url : str):
    session = HTMLSession()
    resp = session.get(url)
        
    resp.html.render()
    #print(resp.html.html)
    return resp.html


def read_targets_file(path : str):
    url_list = []
    try:
        file = open(path,"r")
    except FileNotFoundError as e:
        print(f"{e}")
        return None

    print(f"opened {path}")
    for line in file.read().splitlines():
        if re.match(r'(http\:\/\/|https\:\/\/|www\.)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?',line) != None:
            url_list.append(line)

    file.close()
    print(f"found {len(url_list)} target URL(s) in file")
    return url_list


def get_targets(input : str):
    file_links = []
    if re.match(r'(http\:\/\/|https\:\/\/|www\.)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}\/(\/\S*)?',input) != None:
        file_links.append(input)
        return file_links
    else:
        file_links = read_targets_file(input)
        return file_links


# Saves image to given path 
# (if savepath=None: Save in current working directory)

def save_img(img,fname : str,savepath : str = None):
    if savepath == None:
        img.save(fname)
        #print("Saving: {}".format(fname))
        return

    fpath = savepath+fname 
    img.save(fpath)
    #print("Saving {} to: {}".format(fname,fpath))
    return

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
    print(f"found/filtered {len(filtered_list)} compatible image URL(s)")
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
