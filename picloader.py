from io import BytesIO
from os import access
import sys
import optparse
import urllib
import requests

from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup as bs


def init_optparser(parser,filetypegroup,sizelimitgroup):

    parser.add_option('-o',action="store") # -o : Output Directory

    filetypegroup.add_option('-g',"--gif",help="Only load .gif Images",action="append_const",const=".gif",dest="chosen_types")   # -a : Get all gif Images
    filetypegroup.add_option('-j',"--jpeg",help="Only load .jpeg Images",action="append_const",const=".jpg",dest="chosen_types") # -j : Get all jpeg Images
    filetypegroup.add_option('-p',"--png",help="Only load .png Images",action="append_const",const=".png",dest="chosen_types")   # -p : Get all png Images

    sizelimitgroup.add_option("--min-size",metavar="WIDTH HEIGHT",
            help="All images sized above the chosen WIDTH and HEIGHT in Pixels, can be combined with --max-size",
            type=int,nargs=2,dest="min_s",default=None)
    sizelimitgroup.add_option("--max-size",metavar="WIDTH HEIGHT",
            help="All images sized below the chosen WIDTH and HEIGHT in Pixels, can be combined with --min-size",
            type=int,nargs=2,dest="max_s",default=None)

def main(argv):

    url = argv[1]
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

    #print("getting images from: " + url)
    img_url_list = get_img_urls(url)
    img_url_list = filter_compat_urls(img_url_list,chosen_types)

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

        except Exception as e:
            print(e)


# Extract all absolute image-source-urls from the html code of given webpage url,
# returns list of image-source-urls

def get_img_urls(url):
    data = bs(requests.get(url).content, "html.parser")
    
    img_urls = []

    for img in tqdm(data.find_all("img"),"Extracting all IMG Urls"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urllib.parse.urljoin(url, img_url)
        img_urls.append(img_url)
        #print("URL: {}".format(img_url))

    print("Found {} Images".format(len(img_urls)))
    return img_urls

def get_img(img_url):
    resp = requests.get(img_url)
    return Image.open(BytesIO(resp.content))


# Save image in given path 
# (if savepath=None: Save in current working directory)
def save_img(img,fname,savepath):
    if savepath == None:
        img.save(fname)
        print("Saving: {}".format(fname))
        return

    fpath = savepath+fname
    img.save(fname)
    print("Saving to: {}".format(fpath))
       

# Functions to filter a list of given Image-URLs for compatible formats
def check_compat(url,compat_types):
    for type in compat_types:
        if url.find(type) != -1:
            return True
    return False

def filter_compat_urls(url_list,compat_types):
    filtered_list = []
    for url in url_list:
        if check_compat(url,compat_types):
            filtered_list.append(url)
    return filtered_list


# Filter images by size
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