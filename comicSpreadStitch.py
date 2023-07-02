import cv2
from zipfile import ZipFile
import os
import shutil

tempPath = "temp"

def main():
	lines = []
	
	with open("pagesToCombine.txt", "r") as pagesFile:
		lines = pagesFile.readlines()
	
	for line in lines:
		manga = False
		bookFileName = ""
		parts = line.split("|")
		bookDir = parts[0]
	
		# check for errors in input
		if not bookDirIsValid(bookDir):
			continue
		pages = convertPageList(parts[1], bookDir)
		if not pages:
			continue
		
		os.chdir(bookDir)
		
		bookFileName = findCBZFile()
		if bookFileName == "":
			print("{} has no CBZ files in it. Check your input.".format(bookDir))
		if not bookFileName:
			continue
		
		with ZipFile(bookFileName, 'r') as zip:
			zip.extractall(path = tempPath)
		
		os.chdir(tempPath)
		imgList = os.listdir()
		# check to see if the image files are in a subdirectory and bring them out if so
		while os.path.isdir(imgList[0]):
			for file in os.listdir(imgList[0]):
				shutil.move(os.path.join(imgList[0], file), file)
			os.rmdir(imgList[0])
			imgList = os.listdir()
		
		if len(parts) > 2 and parts[2].strip() == "manga":
			manga = True
		processPages(imgList, pages, manga)
		
		imgList = os.listdir()
		os.chdir("..")
		os.rename(bookFileName, bookFileName + "_old")
		
		# create new CBZ file with the combined pages
		with ZipFile(bookFileName, 'w') as newZip:
			for file in imgList:
				filePath = os.path.join(tempPath, file)
				newZip.write(filePath, arcname = file)
				os.remove(filePath)
		
		os.rmdir(tempPath)
		
		printSuccess(bookFileName, pages)
	
	print("{} books evaluated. See output above for results.\n".format(len(lines)))

def processPages(imgList, pageList, manga):
	for page in pageList:
		# rotate without stitching
		if page[1] == "l" or page[1] == "r":
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
				combImg = cv2.hconcat([img2, img1])
			else:
				combImg = cv2.hconcat([img1, img2])
			
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

def printSuccess(bookFileName, pagesList):
	pagesString = ""
	pagesDeleted = 0
	if pagesList[0][0] == 0 and len(pagesList) == 1:
		pagesString = "the back cover"
		del pagesList[0]
	elif pagesList[0][0] == 0 and len(pagesList) > 1:
		pagesString = "the back cover and "
		del pagesList[0]
	numPages = len(pagesList)
	if numPages == 1:
		pagesString += "page {}".format(pagesList[0][0])
	elif numPages == 2:
		if not pagesList[0][1] == "l" and not pagesList[0][1] == "r":
			pagesDeleted = 1
		pagesString += "pages {} and {}".format(pagesList[0][0], pagesList[1][0] - pagesDeleted)
	elif numPages > 2:
		pagesString += "pages "
		for i in range(numPages):
			if i == numPages - 1:
				pagesString += "{}".format(pagesList[i][0] - pagesDeleted)
				# Not incrementing pagesDeleted because there's no more for it to affect
			elif i == numPages - 2:
				pagesString += "{}, and ".format(pagesList[i][0] - pagesDeleted)
				if not pagesList[i][1] == "l" and not pagesList[i][1] == "r":
					pagesDeleted += 1
			else:
				pagesString += "{}, ".format(pagesList[i][0] - pagesDeleted)
				if not pagesList[i][1] == "l" and not pagesList[i][1] == "r":
					pagesDeleted += 1
	
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
			if not lastChar == "r" and not lastChar == "s" and not lastChar == "l" and not lastChar == "m":
				print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.".format(bookDir))
				return False
			page = page[:-1]
		else:
			lastChar = ""
		if not page.isdigit():
			print("Page list for {} contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.".format(bookDir))
			return False
		else:
			pageIntList.append([int(page), lastChar])
	
	pageIntList.sort()
	
	return pageIntList

def findCBZFile():
	bookFiles = os.listdir()
	bookFileName = ""
	for file in bookFiles:
		filename, extension = os.path.splitext(file)
		if extension == ".cbz":
			bookFileName = file
		if extension == ".cbz_old":
			print("{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n".format(os.getcwd()))
			return False
	
	return bookFileName

if __name__ == "__main__":
	main()
	
# some lines of code that might be useful for debugging at some point

# print(os.getcwd())

# cv2.imshow("Combined image", combImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
