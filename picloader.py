import io
import sys
import optparse
import urllib
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup as bs


def main(argv):
    url = argv[1]
    savepath = None

    parser = optparse.OptionParser()
    parser.add_option('-o',action="store") # -o : Output Directory
    parser.add_option('-a',action="store") # -a : Get all types of Images

    options, remainder = parser.parse_args()

    savepath = options.o

    print("got: " + url)
    img_url_list = get_img_urls(url)
    print("downloading...")

    for img_url in img_url_list:
        try: 
            if img_url.find(".jpg") != -1 or img_url.find(".png") != -1:
                dl_raw(img_url,savepath)
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

def dl_raw(img_url,savepath):
    resp = requests.get(img_url,stream=True)
    img_b = io.BytesIO(resp.content)

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