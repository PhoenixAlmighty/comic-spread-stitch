#	Comic Spread Stitch - for making digital comic books easier to read
#	Copyright (C) 2024 Reed Mauzy
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.

from zipfile import ZipFile
import os
import shutil
import argparse
import math
import logging
import traceback
import datetime

logger = logging.getLogger(__name__)

tempPath = "temp"
newPath = "new"

def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("book", help = "The absolute file path of the ePub you want to convert to CBZ")
    args = parser.parse_args()
    logging.basicConfig(filename = "run.log", level = logging.INFO)
    logger.info(f"Running at {datetime.datetime.now()}")
    logger.debug(f"Book to convert to CBZ is {args.book}")
    try:
        result, reason = convertEpubToCbz(args.book)
        if not result:
            logger.info("Processing complete")
        else:
            logger.warning(reason)
        print(reason)
    except Exception as err:
        out = f"Error occurred while processing\n{traceback.format_exc()}"
        logger.error(out)
        print(out)

def convertEpubToCbz(book):
    [root, ext] = os.path.splitext(book)
    if ext.lower() != ".epub":
        return 1, f"{book} is not an ePub."

    bookDir = os.path.dirname(book)
    logger.debug(f"bookDir is {bookDir}")
    bookEpub = os.path.basename(book)
    logger.debug(f"bookEpub is {bookEpub}")
    os.chdir(bookDir)
    logger.debug(f"Changed directory into {os.getcwd()}")

    with ZipFile(bookEpub, "r") as zip:
        zip.extractall(path = tempPath)
    logger.debug(f"Extracted ZIP archive to {tempPath}")

    os.chdir(tempPath)
    logger.debug(f"Changed directory into {os.getcwd()}")
    docDir, opfFile = findOpfEnterDoc(bookDir, tempPath)
    if not opfFile:
        return 1, docDir
    logger.debug(f"docDir is {docDir}")
    logger.debug(f"opfFile is {opfFile}")

    # get manifest and spine from OPF file
    manifest, spine = getManifestAndSpine(opfFile)
    logger.debug(f"Manifest is {manifest}")
    logger.debug(f"Spine is {spine}")

    # go through spine and grab image filenames from the manifest
    imgs = getImageFilenames(manifest, spine)
    logger.debug(f"Image list is {imgs}")

    os.chdir(bookDir)
    logger.debug(f"Changed directory into {os.getcwd()}")
    docPath = os.path.join(tempPath, docDir)
    logger.debug(f"docPath is {docPath}")
    cbzFileName = os.path.basename(root) + ".cbz"
    logger.debug(f"cbzFileName is {cbzFileName}")

    # put pages into CBZ file
    buildCbzFile(imgs, docPath, cbzFileName)
    logger.info("CBZ file written to disk")

    # clean up
    shutil.rmtree(tempPath)
    logger.debug(f"{tempPath} deleted")

    return 0, f"{bookEpub} converted to CBZ."

# working directory should be in the extracted ePub directory before this is called
def getDocDir():
    dirList = os.listdir()
    for file in dirList:
        if file not in ["META-INF", "mimetype"] and os.path.isdir(file):
            return file
    else:
        return False

# working directory should be in the ePub's document directory before this is called
def findOpfFile():
    dirList = os.listdir()
    for file in dirList:
        fileExt = os.path.splitext(file)[1]
        if fileExt.lower() == ".opf":
            return file
    else:
        return False

# currently returns spine as a list of idrefs
# and manifest as a dict with ids as keys and hrefs as values
# could be changed to return more info if more is needed in the future
def getManifestAndSpine(opfFile):
    lines = []
    with open(opfFile, "r", encoding = 'utf-8') as opf:
        lines = opf.readlines()
    logger.debug("Read in lines from OPF file")

    manifest = {}
    spine = []
    for line in lines:
        if "<itemref " in line:
            spine.append(getHtmlAttributeValue(line, "idref"))
        elif "<item " in line:
            manifest[getHtmlAttributeValue(line, "id")] = getHtmlAttributeValue(line, "href")

    return manifest, spine

# manifest should be a dict, spine should be a list containing only keys in manifest
def getImageFilenames(manifest, spine):
    imgs = []
    for itemref in spine:
        lines = []
        href = manifest[itemref]
        with open(href, "r") as xhtml:
            lines = xhtml.readlines()
        for line in lines:
            if "<img " in line:
                img = getHtmlAttributeValue(line, "src")

                # get the file path to the image from the document directory
                href = href[:href.rfind("/", 0, -1) + 1]
                while img.find("../") == 0:
                    img = img[3:]
                    href = href[:href.rfind("/", 0, -1) + 1]
                imgs.append(href + img)

    return imgs

# working directory should be 1 level up from the target ePub
def buildCbzFile(imgs, docPath, cbzFileName):
    newImgNumber = 0
    numDigits = math.ceil(math.log(len(imgs), 10))
    with ZipFile(cbzFileName, "w") as cbz:
        for img in imgs:
            imgPath = os.path.join(docPath, img)
            newImgName = ("{:0" + str(numDigits) + "d}").format(newImgNumber) + os.path.splitext(img)[1]
            cbz.write(imgPath, arcname = newImgName)
            newImgNumber += 1

def getHtmlAttributeValue(tag, attr):
    firstQuoteIndex = tag.find("\"", tag.find(attr))
    if firstQuoteIndex != -1:
        return tag[firstQuoteIndex + 1 : tag.find("\"", firstQuoteIndex + 1)]
    firstQuoteIndex = tag.find("\'", tag.find(attr))
    return tag[firstQuoteIndex + 1 : tag.find("\'", firstQuoteIndex + 1)]

def findOpfEnterDoc(bookDir, tempPath):
    # check whether OPF file is in the top-level directory
    docDir = ""
    opfFile = findOpfFile()
    if not opfFile:
        # find and enter the document folder
        docDir = getDocDir()
        if not docDir:
            os.chdir(bookDir)
            logger.debug(f"Changed directory into {os.getcwd()}")
            shutil.rmtree(tempPath)
            logger.debug(f"{tempPath} deleted")
            return "Provided ePub has no document directory.", False
        os.chdir(docDir)
        logger.debug(f"Changed directory into {os.getcwd()}")

        # find the OPF file
        opfFile = findOpfFile()
        if not opfFile:
            os.chdir(bookDir)
            logger.debug(f"Changed directory into {os.getcwd()}")
            shutil.rmtree(tempPath)
            logger.debug(f"{tempPath} deleted")
            return "Provided ePub has no OPF file.", False

    return docDir, opfFile

# currently not used, but was useful for something else and could be useful elsewhere
# gets whatever is inside the outermost tag
# only works for tags that are not self-closing
def getInnerTagContent(text):
    # tag type is whatever is between the first < and the first space
    tagType = text[text.find("<") + 1:text.find(" ")]
    # what's inside the tag is whatever is between the first > after the tag type and the closing tag
    return text[text.find(">", text.find(tagType)) + len(tagType):text.find(f"</{tagType}>")]

if __name__ == "__main__":
    main()
