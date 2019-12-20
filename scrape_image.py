from selenium import webdriver
import os
import time
import argparse
import requests
import io
from PIL import Image
import hashlib

DRIVER_PATH = './chromedriver/chromedriver'
#os.chmod(DRIVER_PATH, 0755)

def getURL(query,maxURL,webdriver, delay):
    def scrollEnd(webdriver):
        webdriver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(delay)

    #google search query
    
    searchURL = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    #load the page
    webdriver.get(searchURL.format(q=query))

    imageURLS = set()
    imageCount = 0
    resultStart = 0
    check = []

    while imageCount < maxURL:
        scrollEnd(webdriver)

        #getImagesThumbnails
        thumbnailResult = webdriver.find_elements_by_css_selector("img.rg_ic")
        numberResult = len(thumbnailResult)

        print("[SEARCH] {} results found.".format(numberResult))

        for img in thumbnailResult[resultStart:numberResult]:
            #click every thumbnail to get the real images
            try:
                img.click()
                time.sleep(delay)

            except Exception:
                continue

            #extract image urls
            actualImages = webdriver.find_elements_by_css_selector("img.irc_mi")
            for actualImage in actualImages :
                if actualImage.get_attribute('src'):
                    imageURLS.add(actualImage.get_attribute('src'))

            imageCount = len(imageURLS)

            if len(imageURLS) >= maxURL:
                print("[RESULT] Found {} image links.".format(len(imageURLS)))
                print("[SYSTEM] Saving Images...")
                time.sleep(1)
                break
            
        else:
            print("[PROCESS] Found {} image links... Looking for more!".format(len(imageURLS)))
            check.append(len(imageURLS))
            time.sleep(1)
            loadMoreButton = webdriver.find_elements_by_css_selector(".kbs")
            if loadMoreButton:
                webdriver.execute_script("document.querySelector('.ksb').click();")

        if(len(check) == 3):
            if check[2] == check[1] && check[2] == check[0]:
                print("[RESULT] No more images can be found")
                print("[SYSTEM] Saving Images...")
                check = []
                time.sleep(1)
                break

        resultStart = len(thumbnailResult)
    
    return imageURLS

def savingImages(folder,url):
    try:
        imageContent = requests.get(url).content

    except Exception as e:
        print("[ERROR] Cannot download {} - Error : {}".format(url,e))
    
    try:
        imageFile = io.BytesIO(imageContent)
        image = Image.open(imageFile).convert('RGB')
        filePath = os.path.join(folder,hashlib.sha1(imageContent).hexdigest()[:10]+'.jpg')

        with open(filePath,'wb') as f:
            image.save(f,"JPEG", quality=100)
        
        print("[SUCCESS] Saved {} as {}".format(url,filePath))
        
    except Exception as e:
        print("[ERROR] Cannot save {} - Error : {}".format(url,e))




if __name__  == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--keyword", required=True)
    ap.add_argument("-t", "--targetFolder", default="./results")
    ap.add_argument("-i", "--image", type=int, default=50)
    ap.add_argument("-d", "--delay", type=float, default=0.5)
    args = vars(ap.parse_args())

    targetFolder = os.path.join(args["targetFolder"],'_'.join(args["keyword"].lower().split(' ')))

    if not os.path.exists(args["targetFolder"]):
        os.makedirs(args["targetFolder"])
    
    with webdriver.Chrome(executable_path = DRIVER_PATH) as wd:
        res = getURL(query = args["keyword"],maxURL = args["image"], webdriver = wd, delay = args["delay"])

    for item in res:
        savingImages(args["targetFolder"],item)