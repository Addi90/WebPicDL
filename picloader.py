import io
from os import access
import sys
import optparse
import urllib
import requests

from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup as bs


def main(argv):

    url = argv[1]
    savepath = None

    parser = optparse.OptionParser()
    parser.add_option('-o',action="store") # -o : Output Directory
    parser.add_option('-a',action="store_true",dest="a") # -a : Get all types of Images
    parser.add_option('-j',action="store_true",dest="j") # -j : Get all jpeg Images
    parser.add_option('-p',action="store_true",dest="p") # -p : Get all png Images

    options, remainder = parser.parse_args()

    savepath = options.o

    print("getting images from: " + url)
    img_url_list = get_img_urls(url)

    try: 
        if options.a:
            print("downloading images")
            dl_all(img_url_list,savepath)

        else:
            if options.j:
                print("downloading JPEGs")
                dl_jpg(img_url_list,savepath)

            if options.p:
                print("downloading PNGs")
                dl_png(img_url_list,savepath)

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


# Download image from url leading to image file and save them in given path 
# (if savepath=None: Save in current working directory)

def dl_jpg(img_urls,savepath):
    for url in img_urls:
        if url.find(".jpg") != -1:
            dl_raw(url,savepath)



def dl_png(img_urls,savepath):
    for url in img_urls:
        if url.find(".png") != -1:
            dl_raw(url,savepath)


def dl_all(img_urls,savepath):
    for url in img_urls:
        dl_raw(url,savepath)

def dl_raw(img_url,savepath):
    resp = requests.get(img_url,stream=True)

    if savepath == None:
        if img_url.find('/'):
            with open(img_url.rsplit('/', 1)[1],"wb") as f:
                f.write(resp.content)
        return

    fpath = savepath+img_url.rsplit('/', 1)[1]
    with open(fpath,"wb") as f:
        print("Writing to: {}".format(savepath+img_url.rsplit('/', 1)[1],"wb") )
        f.write(resp.content)

if __name__ == "__main__":
    main(sys.argv)