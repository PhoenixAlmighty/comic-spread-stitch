import cv2
from zipfile import ZipFile
import os
import shutil
import numpy as np
import epubToCbz
import argparse

tempPath = "temp"

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--overlap", type=int, default=50, help="number of columns to check for overlap")
	args = parser.parse_args()
	lines = []
	processed = 0
	skipped = 0
	errors = 0
	
	with open("pagesToCombine.txt", "r") as pagesFile:
		lines = pagesFile.readlines()
	
	for line in lines:
		try:
			bookDir = ""
			parts = line.split("|")
			bookDir = parts[0]
			manga, backedup, epub, rightlines, unknownFlag = getBookFlags(parts[2:])
			pageNumbersNotPresent = (len(parts) >= 2 and parts[1].strip() == "") or len(parts) < 2
			
			os.chdir(bookDir)
			
			bookFileName = findBookFile(backedup, epub)
			if bookFileName == "":
				print("{} has no {} files in it. Check your input.".format(bookDir, "ePub" if epub else "CBZ"))
			if not bookFileName:
				skipped += 1
				continue
			
			if pageNumbersNotPresent and epub:
				epubToCbz.convertEpubToCbz(os.path.join(bookDir, bookFileName))
				processed += 1
				continue
			
			if pageNumbersNotPresent:
				print("The line for {} is missing page numbers.".format(bookDir.strip()))
				skipped += 1
				continue
			if unknownFlag:
				print("Unknown flag detected for {}. Skipping.".format(bookDir))
				skipped += 1
				continue
		
			# check for errors in input
			if not bookDirIsValid(bookDir):
				skipped += 1
				continue
			pages = convertPageList(parts[1], bookDir)
			if not pages:
				skipped += 1
				continue
			
			with ZipFile(bookFileName, 'r') as zip:
				zip.extractall(path = tempPath)
			
			os.chdir(tempPath)
			
			imgList = []
			if not epub:
				imgList = getCbzImgs()
			else:
				docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
				if not opfFile:
					skipped += 1
					print("Skipping {}.".format(bookFileName))
					continue
				manifest, spine = epubToCbz.getManifestAndSpine(opfFile)
				imgList = epubToCbz.getImageFilenames(manifest, spine)
			
			# imgList = os.listdir()
			# # check to see if the image files are in a subdirectory and bring them out if so
			# while os.path.isdir(imgList[0]):
				# for file in os.listdir(imgList[0]):
					# shutil.move(os.path.join(imgList[0], file), file)
				# os.rmdir(imgList[0])
				# imgList = os.listdir()
			
			# check whether imgList is long enough to account for all of pages
			if (pages[-1][1] in ["l", "r", "d"] and len(imgList) < pages[-1][0]) or (not (pages[-1][1] in ["l", "r", "d"]) and len(imgList) < pages[-1][0] + 1):
				print("{} skipped because the last page to process is past the end of the book.".format(bookDir))
				skipped += 1
				os.chdir(bookDir)
				shutil.rmtree(tempPath)
				continue
			
			if rightlines:
				removeRightLines(imgList)
			
			imgList = processPages(imgList, pages, manga, args.overlap)
			
			# this if statement may not be necessary given that processPages returns imgList
			if not epub:
				imgList = os.listdir()
			os.chdir(bookDir)
			if not backedup and not epub:
				os.rename(bookFileName, bookFileName + "_old")
			
			# create new CBZ file with the combined pages
			if epub:
				epubToCbz.buildCbzFile(imgList, os.path.join(tempPath, docDir), bookFileName[:-4] + "cbz")
			else:
				with ZipFile(bookFileName, 'w') as newZip:
					for file in imgList:
						filePath = os.path.join(tempPath, file)
						newZip.write(filePath, arcname = file)
			
			shutil.rmtree(tempPath)
			
			printSuccess(bookFileName, pages)
			processed += 1
		except Exception as err:
			errors += 1
			if bookDir == "":
				print("Error occurred before book directory could be read in. Error message:\n", err)
			else:
				print("Error occurred while processing {}. Error message:\n".format(bookDir),err)
	
	print("{} books processed, {} skipped, and {} errors. See output above for results.\n".format(processed, skipped, errors))

def processPages(imgList, pageList, manga, columns):
	for page in pageList:
		# delete page
		if page[1] == "d":
			os.remove(imgList[page[0] - 1])
		
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
				combImg = stitchPages(img2, img1, columns)
			else:
				# combImg = cv2.hconcat([img1, img2])
				combImg = stitchPages(img1, img2, columns)
			
			# rotate if needed
			if page[1] == "m":
				# rotate left
				combImg = cv2.rotate(combImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
			elif page[1] == "s":
				# rotate right
				combImg = cv2.rotate(combImg, cv2.ROTATE_90_CLOCKWISE)
			
			# overwrite the first page with the combined pages
			cv2.imwrite(imgList[page[0] - 1], combImg)
			
			# remove the second page so I don't see it again separately from the combined pages
			# unless I'm combining the front and back covers, in which case the front cover gets to stay as it is
			if not page[0] == 0:
				os.remove(imgList[page[0]])
	
	for page in reversed(pageList):
		if page[1] == "d":
			del imgList[page[0] - 1]
		elif page[1] in ["", "m", "s"] and not page[0] == 0:
			del imgList[page[0]]
	
	return imgList

def stitchPages(leftImg, rightImg, columns):
	if columns == 0:
		return cv2.hconcat([leftImg, rightImg])
	else:
		columns = (columns * -1) - 1
		for i in range(-1, columns, -1):
			if not np.bitwise_xor(leftImg[:, i], rightImg[:, 0]).any():
				return cv2.hconcat([leftImg[:, :i], rightImg])
				break
		else:
			return cv2.hconcat([leftImg, rightImg])

def printSuccess(bookFileName, pagesList):
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
		print("{} has had {} pages deleted.".format(bookFileName, pagesDeleted))
		return
	
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
		pagesString += "page {}".format(modifiedPagesList[0])
	
	# 2 non-back cover pages
	elif pagesModified == 2:
		pagesString += "pages {} and {}".format(modifiedPagesList[0], modifiedPagesList[1])
	
	# More than 2 non-back cover pages
	elif pagesModified > 2:
		pagesString += "pages "
		for i in range(pagesModified):
			
			# Last page
			if i == pagesModified - 1:
				pagesString += "{}".format(modifiedPagesList[i])
			
			# Second to last page
			elif i == pagesModified - 2:
				pagesString += "{}, and ".format(modifiedPagesList[i])
			
			# At least 2 pages remaining
			else:
				pagesString += "{}, ".format(modifiedPagesList[i])
	
	print("{} successfully altered on {}.".format(bookFileName, pagesString))

def bookDirIsValid(bookDir):
	if bookDir == "":
		print("No book directory on this line. Check your input.")
		return False
	elif not os.path.exists(bookDir):
		print(bookDir + " does not exist. Check your filepath.")
		return False
	
	return True

def convertPageList(pageString, bookDir):
	# validate that input has pages to combine
	if pageString == "":
		print("{} has no pages to combine. Check your input.".format(bookDir))
		return False
	
	# add pages to list of ints while validating that each page has a number and, if any modifiers, ones that match what's defined
	pageStringList = pageString.split(",")
	pageIntList = []
	for page in pageStringList:
		page = page.strip()
		lastChar = page[-1]
		if not lastChar.isdigit():
			if not lastChar in ["r", "s", "l", "m", "d"]:
				print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.".format(bookDir))
				return False
			page = page[:-1]
		else:
			lastChar = ""
		
		if lastChar == "d":
			# Check to see if it's a range
			if "-" in page:
				rangePages = page.split("-")
				for rangePage in rangePages:
					if not rangePage.isdigit():
						print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.".format(bookDir))
						return False
				for i in range(int(rangePages[0]), int(rangePages[1]) + 1):
					pageIntList.append([i, "d"])
			elif page.isdigit():
				pageIntList.append([int(page), lastChar])
			else:
				print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.".format(bookDir))
				return False
		elif not page.isdigit():
			print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.".format(bookDir))
			return False
		else:
			pageIntList.append([int(page), lastChar])
	
	pageIntList.sort()
	
	return pageIntList

def findBookFile(backedup, epub):
	bookFiles = os.listdir()
	bookFileName = ""
	backupFound = False
	ext = ""
	backupExt = ""
	if epub:
		ext = ".epub"
		backupExt = ".epub_old"
	else:
		ext = ".cbz"
		backupExt = ".cbz_old"
	for file in bookFiles:
		filename, extension = os.path.splitext(file)
		if not backedup:
			if extension == ext:
				bookFileName = file
			if extension == backupExt:
				print("{} contains a backup from a previous run. As such, this book will be skipped. Try again after either deleting the {}_OLD file or adding \"backedup\" as a flag on the input.\n".format(os.getcwd(), "EPUB" if epub else "CBZ"))
				return False
		else:
			if extension == ext:
				bookFileName = file
			if extension == backupExt:
				backupFound = True
	
	if backedup and not backupFound:
		print("{} had the backedup flag set, but no backup was found. Remove the backedup flag for this directory to process the book normally.\n".format(os.getcwd()))
		return False
	
	return bookFileName

def getBookFlags(flags):
	manga = False
	backedup = False
	epub = False
	rightlines = False
	unknownFlag = False
	# Parse book flags
	for flag in flags:
		flag = flag.strip()
		if flag == "manga":
			manga = True
		elif flag == "backedup":
			backedup = True
		elif flag == "epub":
			epub = True
		elif flag == "rightlines":
			rightlines = True
		else:
			unknownFlag = True
	return manga, backedup, epub, rightlines, unknownFlag

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

# print(os.getcwd())

# cv2.imshow("Combined image", combImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
