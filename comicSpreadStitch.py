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

import cv2
from zipfile import ZipFile
import os
import shutil
import numpy as np
import epubToCbz
import processPdf
import argparse
import traceback
import logging
import datetime

tempPath = "temp"
logger = logging.getLogger(__name__)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-o", "--overlap", type=int, default=50, help="number of columns to check for overlap")
	parser.add_argument("-c", "--compression", type=int, default=75, help="fuzz factor for compression artifacts")
	args = parser.parse_args()
	logging.basicConfig(filename = 'run.log', level = logging.INFO)
	processed = 0
	skipped = 0
	errors = 0

	with open("pagesToProcess.txt", "r") as pagesFile:
		lines = pagesFile.readlines()

	for line in lines:
		result, reason = processBook(line, args.overlap, args.compression)
		match result:
			case 0:
				processed += 1
			case 1:
				skipped += 1
			case 2:
				errors += 1
			case _:
				print("Unexpected result for book")
		print(reason)

	print(f"{processed} books processed, {skipped} skipped, and {errors} errors. See output above for results.\n")


def processBook(line, overlap = 50, compression = 75):
	bookDir = ""
	try:
		parts = line.split("|")
		bookDir = parts[0]
		validBookDir, reason = bookDirIsValid(bookDir)
		if not validBookDir:
			return 1, reason
		logging.basicConfig(force = True, filename = os.path.join(bookDir, "run.log"), level = logging.INFO)
		logger.info(f"Running at {datetime.datetime.now()}")
		logger.debug(f"Overlap checking is {overlap} columns")
		logger.debug(f"Maximum allowable compression fuzz is {compression}")
		logger.info(f"Line is {line}")
		manga, backedup, epub, pdf, rightlines, unknownFlag = getBookFlags(parts[2:])
		logger.debug(f"manga = {manga}")
		logger.debug(f"backedup = {backedup}")
		logger.debug(f"rightlines = {rightlines}")
		logger.debug(f"unknownFlag = {unknownFlag}")
		if unknownFlag:
			logger.warning("Skipping because there's an unknown flag")
			return 1, f"Unknown flag detected for {bookDir}. Skipping."
		pageNumbersNotPresent = (len(parts) >= 2 and parts[1].strip() == "") or len(parts) < 2
		logging.debug(f"Page numbers are{' not' if pageNumbersNotPresent else ''} present")

		os.chdir(bookDir)
		logger.debug(f"Changed directory into {os.getcwd()}")

		if epub:
			bookFileType = "ePub"
		elif pdf:
			bookFileType = "PDF"
		else:
			bookFileType = "CBZ"
		logger.debug(f"Book file type is {bookFileType}")
		validBookFile, bookFileName = findBookFile(backedup, epub, pdf)
		if not validBookFile:
			logger.warning(f"Skipping book because book filename is not valid. Message is: {bookFileName}")
			return 1, bookFileName
		logger.debug(f"Book filename is {bookFileName}")

		if pageNumbersNotPresent and epub:
			return epubToCbz.convertEpubToCbz(os.path.join(bookDir, bookFileName))

		if pageNumbersNotPresent and pdf:
			logger.warning("Skipping because conversion from PDF to CBZ in main app are not permitted — use pdfToCbz.py instead")
			return 1, f"Skipping {bookFileName} because conversion from PDF to CBZ doesn't always work the way you want it to. If you want to try anyway, please use the pdfToCbz.py script. Just be sure to check the output afterwards."

		# This should not be reached if pageNumbersNotPresent and epub, as there is a return statement in that if block
		if pageNumbersNotPresent and rightlines:
			logger.info("Only requesting to remove right lines")
			with ZipFile(bookFileName, 'r') as zipf:
				zipf.extractall(path = tempPath)
			os.chdir(tempPath)
			logger.debug(f"Changed directory into {os.getcwd()}")
			imgList = getCbzImgs()
			logger.debug(f"Image list is {imgList}")
			removeRightLines(imgList)
			logger.debug("Right lines removed")
			os.chdir(bookDir)
			logger.debug(f"Changed directory into {os.getcwd()}")
			if not backedup:
				os.rename(bookFileName, bookFileName + "_old")
				logger.debug("Backup made")
			else:
				logger.debug("backedup flag is set, so no backup made")
			with ZipFile(bookFileName, 'w') as newZip:
				for file in imgList:
					filePath = os.path.join(tempPath, file)
					newZip.write(filePath, arcname = file)
			logger.debug(f"{bookFileName} has been written to disk")
			shutil.rmtree(tempPath)
			logger.debug(f"{tempPath} deleted")
			logger.info("Right lines removed from book")
			logger.info("Processing complete")
			return 0, f"{bookFileName} has had the right lines removed."

		if pageNumbersNotPresent:
			logger.warning("Skipping because no page numbers and no flags to make that acceptable")
			return 1, f"The line for {bookDir.strip()} is missing page numbers. Skipping."

		# check for errors in input
		pages, reason = convertPageList(parts[1], bookDir)
		if not pages:
			logger.warning(reason)
			return 1, reason
		logger.debug(f"Page list is {pages}")

		if pdf:
			status, reason = processPdf.processPdf(bookFileName, pages, manga, backedup)
			if status:
				logger.warning(reason)
				return status, reason
			else:
				logger.info("Processing complete")
				return 0, getResultString(bookFileName, pages)

		with ZipFile(bookFileName, 'r') as zipf:
			zipf.extractall(path = tempPath)
		logger.debug(f"Extracted ZIP archive to {tempPath}")

		os.chdir(tempPath)
		logger.debug(f"Changed directory into {os.getcwd()}")

		if not epub:
			imgList = getCbzImgs()
		else:
			docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
			if not opfFile:
				logger.warning("Skipping book because the OPF file could not be found")
				return 1, f"Skipping {bookFileName} because the OPF file could not be found."
			manifest, spine = epubToCbz.getManifestAndSpine(opfFile)
			logger.debug(f"Manifest is {manifest}")
			logger.debug(f"Spine is {spine}")
			imgList = epubToCbz.getImageFilenames(manifest, spine)
		logger.debug(f"Image list is {imgList}")

		# imgList = os.listdir()
		# # check to see if the image files are in a subdirectory and bring them out if so
		# while os.path.isdir(imgList[0]):
		# for file in os.listdir(imgList[0]):
		# shutil.move(os.path.join(imgList[0], file), file)
		# os.rmdir(imgList[0])
		# imgList = os.listdir()

		# check whether imgList is long enough to account for all of pages
		if (pages[-1][1] in ["l", "r", "d"] and len(imgList) < pages[-1][0]) or (
				not (pages[-1][1] in ["l", "r", "d"]) and len(imgList) < pages[-1][0] + 1):
			logger.warning("Book skipped because the last page to process is past the end of the book")
			os.chdir(bookDir)
			logger.debug(f"Changed directory into {os.getcwd()}")
			shutil.rmtree(tempPath)
			logger.debug(f"{tempPath} deleted")
			return 1, f"{bookDir} skipped because the last page to process is past the end of the book."

		if rightlines:
			removeRightLines(imgList)
			logger.info("Right lines removed from book")

		imgList = processPages(imgList, pages, manga, overlap, compression)
		logger.info("Pages processed")
		logger.debug(f"Image list is {imgList}")

		# this if statement may not be necessary given that processPages returns imgList
		if not epub:
			imgList = os.listdir()
			logger.debug(f"Image list is {imgList}")
		os.chdir(bookDir)
		logger.debug(f"Changed directory into {os.getcwd()}")
		if not backedup and not epub:
			os.rename(bookFileName, bookFileName + "_old")
			logger.debug("Backup created")
		elif epub:
			logger.debug("Backup not created because the input is ePub and the output is CBZ")
		else:
			logger.debug("Backup not created because a backup already exists")

		# create new CBZ file with the combined pages
		if epub:
			epubToCbz.buildCbzFile(imgList, os.path.join(tempPath, docDir), bookFileName[:-4] + "cbz")
		else:
			with ZipFile(bookFileName, 'w') as newZip:
				for file in imgList:
					filePath = os.path.join(tempPath, file)
					newZip.write(filePath, arcname = file)
		logger.info("CBZ written to disk")

		shutil.rmtree(tempPath)
		logger.debug(f"{tempPath} deleted")

		logger.info("Processing complete")
		return 0, getResultString(bookFileName, pages)

	except Exception as err:
		if bookDir == "":
			reason = f"Error occurred before book directory could be read in.\n{traceback.format_exc()}"
		else:
			reason = f"Error occurred while processing {bookDir}.\n{traceback.format_exc()}"
		logger.error(reason)
		return 2, reason

def processPages(imgList, pageList, manga, columns, compressionFuzz):
	for page in pageList:
		# delete page
		if page[1] == "d":
			os.remove(imgList[page[0] - 1])
			logger.info(f"Deleted page {page[0]}")
		
		# rotate without stitching
		elif page[1] in ["l", "r"]:
			# read in the page I want
			img = cv2.imread(imgList[page[0] - 1])
			
			if page[1] == "l":
				# rotate left
				img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
			elif page[1] == "r":
				# rotate right
				img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
			
			# save image
			cv2.imwrite(imgList[page[0] - 1], img)
			logger.info(f"Rotated page {page[0]} {'counterclockwise' if page[1] == 'l' else 'clockwise'}")
		
		# stitch and possibly rotate
		else:
			# read in the two pages I want to combine
			# this is page - 1 and page because python lists are 0-indexed and the page numbers are 1-indexed
			# print("{}, {}".format(page - 1, page))
			img1 = cv2.imread(imgList[page[0] - 1])
			img2 = cv2.imread(imgList[page[0]])
			
			# horizontally concatenate the two pages
			if manga:
				# combImg = cv2.hconcat([img2, img1])
				combImg = stitchPages(img2, img1, columns, compressionFuzz)
			else:
				# combImg = cv2.hconcat([img1, img2])
				combImg = stitchPages(img1, img2, columns, compressionFuzz)
			
			# rotate if needed
			if page[1] == "m":
				# rotate left
				combImg = cv2.rotate(combImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
			elif page[1] == "s":
				# rotate right
				combImg = cv2.rotate(combImg, cv2.ROTATE_90_CLOCKWISE)
			
			# overwrite the first page with the combined pages
			cv2.imwrite(imgList[page[0] - 1], combImg)
			if page[1] in ['m', 's']:
				logger.info(f"Stitched together pages {page[0]} and {page[0] + 1} and rotated them {'counterclockwise' if page[1] == 'm' else 'clockwise'}")
			else:
				logger.info(f"Stitched together pages {page[0]} and {page[0] + 1}")
			
			# remove the second page so I don't see it again separately from the combined pages
			# unless I'm combining the front and back covers, in which case the front cover gets to stay as it is
			if not page[0] == 0:
				os.remove(imgList[page[0]])
				logger.debug(f"Removed page {page[0] + 1}")
	
	for page in reversed(pageList):
		if page[1] == "d":
			del imgList[page[0] - 1]
		elif page[1] in ["", "m", "s"] and not page[0] == 0:
			del imgList[page[0]]
	
	return imgList

def stitchPages(leftImg, rightImg, columns, compressionFuzz):
	if columns == 0:
		logger.debug("Stitched pages together with no overlap checking")
		return cv2.hconcat([leftImg, rightImg])
	else:
		negcolumns = (columns * -1) - 1
		for i in range(-1, negcolumns, -1):
			# account for fuzz factor for compression artifacts
			# cast ndarrays as int16 because they're uint8 by default, which leads to wrong values when I should get negative ones
			if np.abs(leftImg[:, i].astype(np.int16) - rightImg[:, 0].astype(np.int16)).max() < compressionFuzz:
				logger.debug(f"Stitched pages together after finding overlap at column {i * -1}")
				return cv2.hconcat([leftImg[:, :i], rightImg])
		else:
			logger.debug(f"Stitched pages together without finding overlap in {columns} columns")
			return cv2.hconcat([leftImg, rightImg])

def getResultString(bookFileName, pagesList):
	pagesString = ""
	pagesDeleted = 0
	modifiedPagesList = []
	
	# Make modifiedPagesList a list of all page numbers in the new file that have been modified and are still there
	for i in range(len(pagesList)):
		if pagesList[i][1] == "d":
			pagesDeleted += 1
		elif pagesList[i][1] in ["l","r"]:
			modifiedPagesList.append(pagesList[i][0] - pagesDeleted)
		else:
			modifiedPagesList.append(pagesList[i][0] - pagesDeleted)
			if pagesList[i][0] != 0:
				pagesDeleted += 1
	
	pagesModified = len(modifiedPagesList)
	
	if pagesModified == 0:
		result = f"{bookFileName} has had {pagesDeleted} pages deleted."
		logger.info(f"Result string is '{result}'")
		return result
	
	if modifiedPagesList[0] == 0:
		
		# Back cover only
		if pagesModified == 1:
			pagesString = "the back cover"
		
		# Back cover and other pages
		elif pagesModified > 1:
			pagesString = "the back cover and "
		del modifiedPagesList[0]
		pagesModified = len(modifiedPagesList)
	
	# 1 non-back cover page
	if pagesModified == 1:
		pagesString += f"page {modifiedPagesList[0]}"
	
	# 2 non-back cover pages
	elif pagesModified == 2:
		pagesString += f"pages {modifiedPagesList[0]} and {modifiedPagesList[1]}"
	
	# More than 2 non-back cover pages
	elif pagesModified > 2:
		pagesString += "pages "
		for i in range(pagesModified):
			
			# Last page
			if i == pagesModified - 1:
				pagesString += str(modifiedPagesList[i])
			
			# Second to last page
			elif i == pagesModified - 2:
				pagesString += f"{modifiedPagesList[i]}, and "
			
			# At least 2 pages remaining
			else:
				pagesString += f"{modifiedPagesList[i]}, "
	
	result = f"{bookFileName} successfully altered on {pagesString}."
	logger.info(f"Result string is '{result}'")
	return result

def bookDirIsValid(bookDir):
	if bookDir == "":
		return False, "No book directory on this line. Check your input."
	elif not os.path.exists(bookDir):
		return False, f"{bookDir} does not exist. Check your filepath."
	
	return True, ""

def convertPageList(pageString, bookDir):
	# validate that input has pages to combine
	if pageString == "":
		return False, f"{bookDir} has no pages to combine. Check your input."
	
	# add pages to list of ints while validating that each page has a number and, if any modifiers, ones that match what's defined
	pageStringList = pageString.split(",")
	pageIntList = []
	for page in pageStringList:
		page = page.strip()
		lastChar = page[-1]
		if not lastChar.isdigit():
			if not lastChar in ["r", "s", "l", "m", "d"]:
				logger.warning(f"{page} is not a correct input")
				return False, f"Page list for {bookDir} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input."
			page = page[:-1]
		else:
			lastChar = ""
		
		if lastChar == "d":
			# Check to see if it's a range
			if "-" in page:
				rangePages = page.split("-")
				for rangePage in rangePages:
					if not rangePage.isdigit():
						logger.warning(f"{page} is not a correct input")
						return False, f"Page list for {bookDir} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input."
				for i in range(int(rangePages[0]), int(rangePages[1]) + 1):
					pageIntList.append([i, "d"])
			elif page.isdigit():
				pageIntList.append([int(page), lastChar])
			else:
				logger.warning(f"{page} is not a correct input")
				return False, f"Page list for {bookDir} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input."
		elif not page.isdigit():
			logger.warning(f"{page} is not a correct input")
			return False, f"Page list for {bookDir} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input."
		else:
			pageIntList.append([int(page), lastChar])
			logger.debug(f"Added {[int(page), lastChar]} to page list")
	
	pageIntList.sort()
	logger.debug("Sorted page list")
	
	return pageIntList, ""

def findBookFile(backedup, epub, pdf):
	bookFiles = os.listdir()
	bookFileName = ""
	backupFound = False
	if epub:
		ext = ".epub"
		backupExt = ".epub_old"
		upperExt = "EPUB"
	elif pdf:
		ext = ".pdf"
		backupExt = ".pdf_old"
		upperExt = "PDF"
	else:
		ext = ".cbz"
		backupExt = ".cbz_old"
		upperExt = "CBZ"
	logger.debug(f"Looking for a {upperExt} file in {os.getcwd()}")
	for file in bookFiles:
		filename, extension = os.path.splitext(file)
		if not backedup:
			if extension == ext:
				bookFileName = file
			if extension == backupExt:
				return False, f"{os.getcwd()} contains a backup from a previous run. As such, this book will be skipped. Try again after either deleting the {upperExt}_OLD file or adding \"backedup\" as an option on the input.\n"
		else:
			if extension == ext:
				bookFileName = file
			if extension == backupExt:
				backupFound = True
	
	if backedup and not backupFound:
		return False, f"{os.getcwd()} had the backedup flag set, but no backup was found. Remove the backedup flag for this directory to process the book normally.\n"

	if bookFileName == "":
		return False, f"{os.getcwd()} has no {upperExt} files in it. Check your input."
	
	return True, bookFileName

def getBookFlags(flags):
	manga = False
	backedup = False
	epub = False
	pdf = False
	rightlines = False
	unknownFlag = False
	# Parse book flags
	for flag in flags:
		flag = flag.strip()
		if flag == "manga":
			manga = True
			logger.debug("Found manga flag")
		elif flag == "backedup":
			backedup = True
			logger.debug("Found backedup flag")
		elif flag == "epub":
			epub = True
			logger.debug("Found epub flag")
		elif flag == "pdf":
			pdf = True
			logger.debug("Found pdf flag")
		elif flag == "rightlines":
			rightlines = True
			logger.debug("Found rightlines flag")
		else:
			unknownFlag = True
			logger.debug(f"Found unknown flag: {flag}")
	return manga, backedup, epub, pdf, rightlines, unknownFlag

def getCbzImgs():
	imgList = os.listdir()
	
	# check to see if the image files are in a subdirectory and bring them out if so
	while os.path.isdir(imgList[0]):
		for file in os.listdir(imgList[0]):
			shutil.move(os.path.join(imgList[0], file), file)
		os.rmdir(imgList[0])
		imgList = os.listdir()
	
	return imgList

def removeRightLines(imgList):
	for img in imgList:
		page = cv2.imread(img)
		page = page[:, :-1]
		cv2.imwrite(img, page)

if __name__ == "__main__":
	main()
	
# some lines of code that might be useful for debugging at some point

# can replace if statement starting with np.abs in stitchPages if I want no differences in that column:
			# if not np.bitwise_xor(leftImg[:, i], rightImg[:, 0]).any():

# print(os.getcwd())

# cv2.imshow("Combined image", combImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
