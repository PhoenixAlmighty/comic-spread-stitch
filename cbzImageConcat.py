import cv2
from zipfile import ZipFile
import os
import shutil

calLibDir = "D:\\Calibre Library\\"
bookDir = os.path.join(calLibDir, "Erik Larsen\\Savage Dragon #203 (1404)\\")
tempPath = "temp"

def main():
	lines = []
	
	with open("pagesToCombine.txt", "r") as pagesFile:
		lines = pagesFile.readlines()
	
	for line in lines:
		backupPresent = False
		bookFileName = ""
		parts = line.split("|")
		bookDir = parts[0]
	
		# check for errors in input
		if not bookDirIsValid(bookDir):
			continue
		pages = convertPageList(parts[1], bookDir)
		if not pages:
			continue
		
		# pages = list(map(int, parts[1].split(",")))
		# pages.sort()
		
		os.chdir(bookDir)
		
		# find CBZ file from book directory
		# check for CBZ_OLD file and skip this book if found
		bookFileName = findCBZFile()
		if not bookFileName:
			print("{} has no CBZ files in it. Check your input.".format(bookDir))
			continue
		
		# bookFiles = os.listdir()
		# for file in bookFiles:
			# filename, extension = os.path.splitext(file)
			# if extension == ".cbz":
				# bookFileName = file
			# if extension == ".cbz_old":
				# backupPresent = True
				# print("{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n".format(bookDir))
				# break
		# if backupPresent:
			# continue
		# if bookFileName == "":
			# print("{} has no CBZ files in it. Check your input.".format(bookDir))
		
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
		
		combinePages(imgList, pages)
		
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
		
		# print success message and pages to check
		# for a in range(len(pages)):
			# pages[a] = pages[a] - a
		# print("{} successfully altered. Check pages {} to make sure it was done right.\n".format(bookFileName, pages))
		printSuccess(bookFileName, pages)
	
	print("{} books evaluated. See output above for results.\n".format(len(lines)))

# TODO: implement manga mode

def combinePages(imgList, pageList):
	for page in pageList:
		# read in the two pages I want to combine
		# this is page - 1 and page because python lists are 0-indexed and the page numbers are 1-indexed
		# print("{}, {}".format(page - 1, page))
		img1 = cv2.imread(imgList[page - 1])
		img2 = cv2.imread(imgList[page])
		
		# horizontally concatenate the two pages
		combImg = cv2.hconcat([img1, img2])
		
		# overwrite the first page with the combined pages
		cv2.imwrite(imgList[page - 1], combImg)
		
		# remove the second page so I don't see it again separately from the combined pages
		# unless I'm combining the front and back covers, in which case the front cover gets to stay as it is
		if not page == 0:
			os.remove(imgList[page])

# Required test cases:
	# Back cover only
	# Back cover + 1 spread
	# Back cover + 2 spreads
	# Back cover + 3 or more spreads
	# 1 spread
	# 2 spreads
	# 3 or more spreads

def printSuccess(bookFileName, pagesList):
	pagesString = ""
	if pagesList[0] == 0 and len(pagesList) == 1:
		pagesString = "the back cover"
		pagesList.del(0)
	elif pagesList[0] == 0 and len(pagesList) > 1:
		pagesString = "the back cover and "
		pagesList.del(0)
	numPages = len(pagesList)
	if numPages == 1:
		pagesString += "page {}".format(pagesList[0])
	elif numPages == 2:
		pagesString += "pages {} and {}".format(pagesList[0], pagesList[1] - 1)
	elif numPages > 2:
		pagesString = "pages "
		for i in range(numPages):
			if i == numPages - 1:
				pagesString += "{}".format(pagesList[i] - i)
			elif i == numPages - 2:
				pagesString += "{}, and ".format(pagesList[i] - i)
			else:
				pagesString += "{}, ".format(pagesList[i] - i)
	
	print("{} successfully altered on {}.".format(bookFileName, pagesString))

# Required test cases:
	# No book directory
	# Book directory that doesn't exist on my computer
	# Book directory that does exist on my computer

def bookDirisValid(bookDir):
	if bookDir == "":
		print("No book directory on this line. Check your input.")
		return False
	elif not os.path.exists(bookDir):
		print(bookDir + " does not exist. Check your filepath.")
		return False
	
	return True

# Required test cases:
	# No pages
	# Letters in list
	# Only numbers in list

def convertPageList(pageString, bookDir):
	if pageString == "":
		print("{} has no pages to combine. Check your input.".format(bookDir))
		return False
	pageStringList = pageString.split(",")
	pageIntList = []
	for page in pageStringList:
		page.strip()
		if not page.isdigit():
			print("Page list for {} contains at least one thing that's not a number. Check your input.".format(bookDir))
			return False
		else:
			pageIntList.append(int(page))
	
	pageIntList.sort()
	
	return pageIntList

# Required test cases:
	# Directory has no CBZ file
	# Directory has a CBZ_OLD file
	# Directory has a CBZ file and no CBZ_OLD file

def findCBZFile():
	bookFiles = os.listdir()
	bookFileName = ""
	for file in bookFiles:
		filename, extension = os.path.splitext(file)
		if extension == ".cbz":
			bookFileName = file
		if extension == ".cbz_old":
			print("{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n".format(bookDir))
			return False
	
	return bookFileName

if __name__ == "__main__":
	main()
	
# some lines of code that might be useful for debugging at some point

# print(os.getcwd())

# cv2.imshow("Combined image", combImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
